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

whitespace = re.compile('[%s]' % re.escape(string.whitespace))
punctuation = re.compile('[%s]' % re.escape(string.punctuation))


def get_firstname_lastname(record):
    "Returns (firstname, lastname,pattern_number) for a given person record"
    firstname, lastname = "", ""
    pattern_number = -1  # the value indicating no match found!
    for p in patterns.name_patterns:
        if p == patterns.pattern_names_8:
            # Special case where we search instead of match
            match_object = p.search(record)
        else:
            match_object = p.match(record)
        if match_object:
            firstname = match_object.group('first').strip().lower()
            lastname = match_object.group('last').strip().lower()
            pattern_number = patterns.name_patterns.index(p)+1
            break  # match found; don't try any more patterns
    return (firstname, lastname, pattern_number)


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


def get_n_grams(s, n=3):
    """
    Returns a *set* (not a list) of n_grams (letter sequences) parsed from 
    an input string.
    """
    n_grams_list = []
    s = re.sub(punctuation, "", s)     # remove punctuation
    s = re.sub(whitespace, "", s)      # remove whitespace
    s = s.lower()                               # lowercase
    pos = 0
    while pos < (len(s) - (n-1)):
        n_grams_list.append(s[pos:pos + n])
        pos = pos + 1
    n_grams_set = set(n_grams_list)             # convert to set to eliminate dupes
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

    if a.email and a.email == b.email:
        # identical emails --> perfect match
        score = 100
    elif (not a.last_name) or (not b.last_name):
        # either last_name is blank --> no basis for a score
        score = 0
    elif a.last_name != b.last_name:
        # different (non-blank) last names --> not a match
        score = 0
    elif (a.last_name == b.last_name) and (a.first_name != b.first_name):
        # Identical lastnames but different first names --> unlikely match
        # Avoid using n_grams in this case to avoid false positives
        score = 10
    elif (a.last_name == b.last_name) and (a.first_name == b.first_name):
        # Identical (non-blank) first AND last names --> a likely match
        score = 80
    else:
        # All other cases, fall back on the jaccard index of the n-grams
        # (n_grams are stored in the db as strings, need to be converted to sets)
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

