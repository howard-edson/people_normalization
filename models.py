#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module: models.py
"""
Use SQLAlchemy to define the data model so it can be implemented as a 
SQL database.
"""

from sqlalchemy import Column, Integer, String, Boolean, Sequence, \
                       create_engine, ForeignKey, UniqueConstraint, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from person_parse import get_firstname_lastname, get_email_name_domain, get_n_grams

Base = declarative_base()

sims = Table("sims", Base.metadata,
    Column("left_person_id", Integer, ForeignKey("person.id"), primary_key=True),
    Column("right_person_id", Integer, ForeignKey("person.id"), primary_key=True)
)


class Person(Base):
    "A person object includes attributes parsed from an input record."
    __tablename__ = 'person'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    ringtail_person_id = Column(Integer, unique=True)
    input_record = Column(String(250), nullable=False, unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100))
    domain = Column(String(100))
    n_grams = Column(String(100))      # comma-delimited list of n-grams from last_name and email_name
    name_pattern = Column(Integer)     # the name pattern that was used to parse first and last name
    sim_group_id = Column(Integer, ForeignKey('sim_group.id'), nullable=True)
    similar_people = relationship("Person",
        secondary=sims,
        primaryjoin=id==sims.c.left_person_id,
        secondaryjoin=id==sims.c.right_person_id)
    
    def __init__(self, rt_id, input_record):
        self.ringtail_person_id = rt_id
        self.input_record = input_record
        self.first_name, self.last_name, self.name_pattern = get_firstname_lastname(self.input_record)
        self.email, self.email_name, self.domain = get_email_name_domain(self.input_record)
        self.n_grams = (','.join(
            get_n_grams(self.last_name) | 
            get_n_grams(self.email_name)))

    def __repr__(self):
        return 'person object: {}'.format(self.input_record)


class Sim_group(Base):
    """
    A sim_group contains a set of people that likely represent the same human person due to their 
    high similarity scores. group id 1 is a special case - the default/misc group, for people
    who don't have any similar people.
    """
    __tablename__ = 'sim_group'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    is_misc = Column(Boolean, default=False, server_default="false")
    # bi-directional one-to-many (e.g. person.sim_group and sim_group.people)
    people = relationship("Person", order_by="Person.id", backref="sim_group")
    # other attributes to add in the future...
    # the canonical representation of this person (aka "title")
    # canonical_name = Column(String(100))
    # flag for whether a human reviewer has confirmed the group is correct and complete
    # reviewed = Column(Boolean, default=False, server_default="false")  


def make_sim_group_1(session):
    "Manually create default sim_group id=1 when database is first created."
    g = Sim_group(id=1, is_misc=True)
    session.add(g)
    session.commit()
    return


if __name__ == "__main__":
    DB_NAME = 'people.db'

    import os
    try:  # delete the db if it exists
        os.remove(DB_NAME)
    except OSError:
        pass

    # create the db file
    engine = create_engine('sqlite:///{}'.format(DB_NAME))
    Base.metadata.create_all(engine)

    # create default sim_group 1
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    make_sim_group_1(session)
    session.close()
