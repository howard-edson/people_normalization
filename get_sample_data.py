#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module: get_sample_data.py
"""
Pull a random sample of people records from an input file.
"""

import sys
import codecs
import random

# check for correct usage and print error message if incorrect.
if len(sys.argv) != 2:
    print """Error. Pass the name of the input file as an argument, e.g. 
#> python run_process.py input_file.csv <enter>"""
    sys.exit()

INPUT_FILE = sys.argv[1]                        # full name with extension
SAMPLE_SIZE = 1000
HEADER_ROW = True                               # first row of input file contains field names?
ENCODING = 'utf-16'                             # 'utf-8', 'latin-1', or 'utf-16' when saved Excel as unicode.txt
INPUT_FILE_NAME = INPUT_FILE.split('.')[0]      # first part of filename only
OUTPUT_FILE_NAME = '{}_test.txt'.format(INPUT_FILE_NAME)
DELIMETER = '\t'


# 1. Read the file into a list of tuples: (person_id, person)
input_record_list = []
with codecs.open(INPUT_FILE, mode="r", encoding=ENCODING) as f:
    count_input_records = 0
    records_processed = dict()  # prevents adding the same record twice if duplicated in INPUT_FILE
    if HEADER_ROW:
        next(f)    # skip first line in input file
    for row in f:
        row = row.split(DELIMETER)
        person_id = row[0]  # the source system ID for the record
        person = row[1].strip()
        if person and not person in records_processed:
            records_processed[person] = 1
            input_record_list.append((person_id, person))
            count_input_records += 1
        else:
            records_processed[person] += 1

for person, count in records_processed.iteritems():
    if count > 1:
        print '{0}:{1}'.format(person, count)

# 2. select a random sample from the list into a new list
sample_list = random.sample(input_record_list, SAMPLE_SIZE)

# 3. write the sample to a pipe-delimited output file
with codecs.open(OUTPUT_FILE_NAME, mode="w", encoding=ENCODING) as outfile:
    outfile.write(u'person_id{}person\n'.format(DELIMETER))        # write header row
    for person in sample_list:
        line = u'{0}{1}{2}\n'.format(person[0], DELIMETER, person[1])
        outfile.write(line)

print '{0} records written to {1}'.format(SAMPLE_SIZE, OUTPUT_FILE_NAME)