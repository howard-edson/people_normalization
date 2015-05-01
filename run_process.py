#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module: run_process.py
"""
Reads people records from an input file, identifies and groups records 
that likely represent the same real-world pesron.

Run from command line, passing name of input file as an argument, e.g.
#> python run_process.py input_file.txt <enter>
"""

import codecs
from person_parse import get_sim_score, same_group, same_names
import sqlalchemy
from sqlalchemy.sql import select
import models
import os, sys

# check for correct usage and print error message if incorrect.
if len(sys.argv) != 2:
    print """Error. Pass the name of the input file as an argument, e.g. 
#> python run_process.py input_file.csv <enter>"""
    sys.exit()

INPUT_FILE = sys.argv[1]                        # full name with extension
HEADER_ROW = True                               # first row of input file contains field names?
ENCODING = 'utf-16'                             # 'utf-8', 'latin-1', or 'utf-16' when saved Excel as unicode.txt
INPUT_FILE_NAME = INPUT_FILE.split('.')[0]      # first part of filename only
DB_NAME = '{}.sqlite'.format(INPUT_FILE_NAME)
OUTPUT_FILE_NAME = '{}_output.txt'.format(INPUT_FILE_NAME)
SCORE_THRESHOLD = 50                            # scores above this level are possible matches
MEASURE_EXEC_TIME = True                        # for measuring and printing execution time
DELIMETER = '\t'

print 'INPUT_FILE: {}'.format(INPUT_FILE)
print 'DB_NAME: {}'.format(DB_NAME)
print 'OUTPUT_FILE_NAME: {}'.format(OUTPUT_FILE_NAME)

if MEASURE_EXEC_TIME:
    import time
    start_time = time.time()

# ** Step 0 **
# Recreate the db file from scratch each time
try: 
    os.remove(DB_NAME)
    print 'Database {} dropped.'.format(DB_NAME)
except IOError:
    print 'No database file found.'

engine = sqlalchemy.create_engine('sqlite:///{}'.format(DB_NAME))
models.Base.metadata.create_all(engine)

# set up the db connection
models.Base.metadata.bind = engine
DBSession = sqlalchemy.orm.sessionmaker(bind=engine)
session = DBSession()

models.make_sim_group_1(session)  # create default sim_group 1
print 'Database {} created.'.format(DB_NAME)


# ** Step 1 **
# Read people records from the input file, instantiate Person objects,
# and save them to the database.
# Note: updated to work with two-column input file on 4/21/15
with codecs.open(INPUT_FILE, mode="r", encoding=ENCODING) as f:
    count_input_records = 0
    records_processed = dict()  # prevents adding the same record twice if duplicated in INPUT_FILE
    if HEADER_ROW:
        # skip first line in input file
        next(f)
    for row in f:
        row = row.split('\t')
        source_id = row[0]  # the source ID for the record
        record = row[1].strip()
        if record and not record in records_processed:
            records_processed[record] = 1
            p = models.Person(source_id, record)
            session.add(p)
            count_input_records += 1
session.commit()
print '{} people records created.'.format(count_input_records)


# ** Step 2 **
# Create sims relationships - this is an O(n^2) algorithm!
count_sims_records = 0
people_recordset = session.query(models.Person).all()
for a_person in people_recordset:
    for b_person in people_recordset:
        if a_person.id != b_person.id:  # don't score a record against itself
            score = get_sim_score(a_person, b_person)
            if score >= SCORE_THRESHOLD:
                # create a sim record by adding b_person to a_person's 'similar_people' attribute
                a_person.similar_people.append(b_person)
                count_sims_records += 1
session.commit()
print '{} sims records created.'.format(count_sims_records)


# ** Step 3 **
# Arrange people records into groups based on sims relationships.
# Records with no sims go into the misc sim_group 1.
people = session.query(models.Person).all()
for person in people:
    if person.sim_group_id:             # person has already been grouped
        continue                        # skip immediately to the next person
    else:
        sims = person.similar_people
        if not sims:                    # person has no sims
            person.sim_group_id = 1     # put person in misc group
            session.add(person)
        else:                           # put person and his sims into a new group
            related_people = [person]
            related_people.extend(sims)
            new_group = models.Sim_group(people=related_people)
            session.add(new_group)
        session.flush()                 # flush session each time (needed?)
session.commit()


# ** Step 3a **
# At this stage there can be a person in a group by himself.
# Those cases should either be moved to another group, or to group 1 (misc).
# 1. Get a list of people alone in a group
people_alone_in_a_group = select([models.Person.id]).\
        group_by(models.Person.sim_group_id).\
        having(sqlalchemy.func.count(models.Person.id) == 1)

single_grouped_people = session.query(models.Person).\
        filter(models.Person.id.in_(people_alone_in_a_group)).\
        all()

for p in single_grouped_people: # for each person alone in a group...
    old_group_id = p.sim_group_id  # the old group to be deleted
    same_grp = same_group(p.similar_people) # an int representing the same group_id, or False
    #  if (all sims are in the same group) AND (all sims have the same first and last name):
    if same_grp and same_names(p.similar_people):
        p.sim_group_id = same_grp  # put this person in the same group as his sims
    else:
        p.sim_group_id = 1  # put him in the misc group
    # either way, delete the now empty group from the groups table
    old_group = session.query(models.Sim_group).filter_by(id=old_group_id).one()
    session.delete(old_group)

group_count = session.query(sqlalchemy.func.count(models.Sim_group.id)).scalar()
print '{} new groups created.'.format(group_count)
session.commit()


## ** Step 4 **
## Write output file - pipe-delimited
people_recordset = session.query(models.Person).\
    order_by(models.Person.sim_group_id.desc(), models.Person.last_name, models.Person.first_name).all()

with codecs.open(OUTPUT_FILE_NAME, mode="w", encoding=ENCODING) as outfile:
    # write header row
    outfile.write(u'person_id{D}input_record{D}sim_group_id{D}first_name{D}last_name{D}email{D}domain{D}full_name\n'.format(D=DELIMETER))

    for person in people_recordset:
        kwargs = {
          'D': DELIMETER,
          'source_person_id': person.source_person_id,
          'input_record': person.input_record, 
          'sim_group_id': person.sim_group_id, 
          'first_name': person.first_name, 
          'last_name': person.last_name, 
          'email': person.email,
          'domain': person.domain,
          'full_name': u'{}, {}'.format(person.last_name, person.first_name).title() if (person.first_name and person.last_name) else u''
        }
        line = u'{source_person_id}{D}{input_record}{D}{sim_group_id}{D}{first_name}{D}{last_name}{D}{email}{D}{domain}{D}{full_name}\n'.format(**kwargs)
        outfile.write(line)

session.close()
if MEASURE_EXEC_TIME:
    end_time = time.time()
    exec_time = end_time - start_time
    if exec_time < 60:
        print '\nProcessed {0} records in {1} seconds.'.format(count_input_records, round(exec_time, 2))
    elif exec_time < 3600:
        print '\nProcessed {0} records in {1} minutes.'.format(count_input_records, round(exec_time/60, 2))
    else:
        print '\nProcessed {0} records in {1} hours.'.format(count_input_records, round(exec_time/3600, 2))
