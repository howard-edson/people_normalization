#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module: person_parse.py

"""
Defines some utility functions for parsing people records, and calculating
similarity scores for pairs of people records based on their features.
"""

import re
import codecs       # to handle unicode characters in input file
import patterns     # my module containing all the regex patterns
import string

def get_firstname_lastname(record):
    "Returns (firstname, lastname) from a given person record"
    firstname, lastname = "", ""
    # try each pattern in order to parse first and last names
    for p in patterns.name_patterns:
        if p == patterns.pattern_names_5:
            match_object = patterns.pattern_names_5.search(record)
            if match_object:
                lastname = match_object.group('last').strip()
        else:
            match_object = p.match(record)
            if match_object:
                firstname = match_object.group('first').strip().lower()
                lastname = match_object.group('last').strip().lower()
        if match_object:
            break  # match found; don't try any more patterns
    #print 'pattern %s' % (patterns.name_patterns.index(p)+1)
    return (firstname, lastname)


def get_email_name_domain(record):
    "Returns (email, name, domain) from a given person record"
    email, name, domain = "", "", ""
    name_match_object = patterns.pattern_email_name.search(record)
    if name_match_object:
        name = name_match_object.group('name').lstrip('<("').lower()

    domain_match_object = patterns.pattern_domain.search(record)
    if domain_match_object:
        domain = domain_match_object.group('domain').rstrip('>)"').lower()
        
    email_match_object = patterns.pattern_email.search(record)
    if email_match_object:
        email = email_match_object.group('email').strip(string.punctuation).lower()

    return (email, name, domain)


def get_firstname_from_email(email):
    """
    Returns a firstname from an email address; used as a fallback when it couldn't 
    be parsed from the whole person record.
    """
    firstname = ""
    name_match_object = patterns.pattern_fname_from_email.search(email)
    if name_match_object:
        firstname = name_match_object.group('first')
    return firstname


def get_n_grams(s, n=3):
    """
    Returns a *set* (not a list) of n_grams (letter sequences) parsed from 
    an input string.
    """
    n_grams_list = []
    s = re.sub(patterns.punctuation, "", s)     # remove punctuation
    s = re.sub(patterns.whitespace, "", s)      # remove whitespace
    s = s.lower()                               # lowercase
    pos = 0
    while pos < (len(s) - (n-1)):
        n_grams_list.append(s[pos:pos + n])
        pos = pos + 1
    n_grams_set = set(n_grams_list)             # convert to set to eliminate dupes
    #n_grams_string = ','.join(n_grams_set)
    return n_grams_set


def get_jaccard_index(set_a, set_b):
    """
    Returns the Jaccard similarity index (0-1) for two sets,
    such as the set of n_grams returned by get_n_grams() in this module.

    The Jaccard index is the number of elements to both sets (the length 
    of the intersection) divided by the total number of elements in both 
    sets (the length of the union).
    """
    intersection = set_a & set_b  # the intersection of two sets
    union = set_a | set_b         # the union of two sets
    if union:
        return (1.0 * len(intersection) / len(union))
    else:
        return 0


def get_sim_score(a, b):
    "Returns a similarity score 0-100 for two person objects and b."
    score = 0

    # Emails are identical; perfect match!
    if a.email and a.email == b.email:
        score = 100
    # Identical first AND last names; likely match! 
    elif (a.last_name and a.last_name == b.last_name) and \
         (a.first_name and a.first_name == b.first_name):
        score = 80
    # Identical lastnames but different first names; NOT a likely match!
    # Avoid using n_grams because you may well get a false positive!
    elif (a.last_name and a.last_name == b.last_name) and \
         (a.first_name != b.first_name) and \
         (len(a.first_name) > 2 or len(b.first_name) > 2) and \
         not (a.first_name in b.first_name or b.first_name in a.first_name):
        score = 20
    # Fall back on the jaccard index of the n-grams
    # (n_grams are stored in the db as strings, need to be converted to sets)
    else:
        score = int(100*(get_jaccard_index(set(a.n_grams.split(',')), set(b.n_grams.split(',')))))
    return score


def same_group(people):
    """
    Takes a list of people objects. If all the people are in the same group,
    then this function returns that group_id. Otherwise it returns False.
    """
    group_id = None
    for person in people:
        if group_id and (group_id != person.sim_group_id):
            return False
        else:
            group_id = person.sim_group_id
    return group_id


def same_names(people):
    """
    Takes a list of people objects. Returns True if they all
    have the same first and last names.
    """
    first_name = None
    last_name = None
    first = True
    for person in people:
        if first:
            first_name = person.first_name
            last_name = person.last_name
            first = False
            continue
        if first_name != person.first_name or last_name != person.last_name:
            return False
        else:
            first_name = person.first_name
            last_name = person.last_name
    return True

