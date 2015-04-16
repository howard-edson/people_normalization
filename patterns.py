#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module: patterns.py

"""
 Each of the regex patterns used in parsing attributes from a person record:
 firstname, lastname, email address, email name, email domain.

 Also creates regex patterns for whitespace and punctuation.
"""
import re
import string

whitespace = re.compile('[%s]' % re.escape(string.whitespace))
punctuation = re.compile('[%s]' % re.escape(string.punctuation))

pattern_names_1 = re.compile(
    # looks for "lastname, firstname [other stuff] 
    # handles names with hyphens or spaces
    # must have comma (lastname, firstname)
    r"""
    \"                        # double quote (must be escaped in re.VERBOSE mode)
    (?P<last>[a-zA-Z-\s]+)    # last name (can include space or hyphen)
    \,                        # comma separator
    \s{1,2}                   # one or two spaces
    (?P<first>[a-zA-Z-\s]+)   # first name (can include space or hyphen)
    .*                        # any other crap
    \"                        # double quote (must be escaped in re.VERBOSE mode)
    """,
    re.UNICODE | re.VERBOSE)


pattern_names_2 = re.compile(
    # looks for "firstname lastname [other stuff]" (between quotes)
    # handles names with hyphens or spaces
    # must NOT have comma (firstname [space] lastname)
    r"""
    \"                        # double quote (must be escaped in re.VERBOSE mode)
    (?P<first>[a-zA-Z-\s]+)   # first name (can include space or hyphen)
    .*                        # any other crap
    \s{1,2}                   # one or two spaces
    (?P<last>[a-zA-Z-\s]+)    # last name (can include space or hyphen)
    \"                        # double quote (must be escaped in re.VERBOSE mode)
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_3 = re.compile(
    # looks for firstname lastname <email@domain.tld> (no quotes)
    r"""
    (?P<first>[a-zA-Z-\s]+)   # first name (can include space or hyphen)
    \s{1,2}                   # one or two spaces
    (?P<last>[a-zA-Z-\s]+)    # last name (can include space or hyphen)
    \s{1,2}                   # one or two spaces
    [<(]                      # start of the email address (which we're ignoring)
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_4 = re.compile(
    # looks for firstname.lastname@domain.tld
    # where separator must exist and can be dot or underscore
    r"""
    (?P<first>[a-zA-Z-]+)     # first name (can include hyphen but not space)
    [._]                      # dot or underscore character
    (?P<last>[a-zA-Z-]+)      # last name (can include hyphen but not space)
    @                         # @ symbol
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_4a = re.compile(
    # looks for "firstname lastname [other stuff]
    r"""
    \"                        # double quote (must be escaped in re.VERBOSE mode)
    (?P<first>[a-zA-Z]+)      # first name 
    \s{1,2}                   # one or two spaces
    (?P<last>[a-zA-Z]+)       # last name
    \s{1,2}                   # one or two spaces
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_5 = re.compile(
    # gets lastname only, from biglongname@domain.tld 
    # (where there is no separator in name, such as a period)
    # use a re.search on this one, not re.match
    r"""
    (?P<last>\w+)             # last name (any alphanumeric chars, but no spaces or periods)
    @                         # @ symbol
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_6 = re.compile(
    # looks for lastname, firstname ONLY! (no quotes, no email)
    r"""
    (?P<last>[a-zA-Z-\s]+)    # last name (can include space or hyphen)
    \,                        # comma separator
    \s{1,2}                   # one or two spaces
    (?P<first>[a-zA-Z-\s]+)   # first name (can include space or hyphen)
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_7 = re.compile(
    # looks for firstname lastname ONLY! (no quotes, no email)
    r"""
    (?P<first>[a-zA-Z-\s]+)    # first name (can include space or hyphen)
    \s{1,2}                    # one or two spaces
    (?P<last>[a-zA-Z-\s]+)     # last name (can include space or hyphen)
    """,
    re.UNICODE | re.VERBOSE)

name_patterns = [pattern_names_1, pattern_names_2, pattern_names_3, 
    pattern_names_4, pattern_names_4a, pattern_names_5, pattern_names_6, pattern_names_7
]

pattern_email_name = re.compile(
    # gets email name from biglongname@domain.tld (where there is no separator in name)
    # use a re.search on this one, not re.match
    # note this returns the '<' if present, which must be stripped in a containing function
    r"""
    (?P<name>\S+)             # email name (any contiguous non-whitespace characters)
    @                         # @ symbol
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_domain = re.compile(
    # gets domain name from biglongname@domain.tld
    # use a re.search on this one, not re.match
    # note this returns the '>' if present, which must be stripped in a containing function
    r"""
    .*                        # anything
    @                         # @ symbol
    (?P<domain>\S+)           # domain (any contiguous non-whitespace chars)
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_email = re.compile(
    # gets email address from a person record
    # use a re.search on this one, not re.match
    # note this returns the () or <> or [] if present, which must be stripped in a containing function
    r"""
    (?P<email>\S+@\S+\.\S+)   # email (must contain exactly one @ followed by text and then at least one . and no whitespace)
    """,
    re.UNICODE | re.VERBOSE)

pattern_fname_from_email = re.compile(
    # looks for firstname.lastname@domain.tld
    # where separator must exist and can be dot or underscore
    r"""
    (?P<first>[0-9a-zA-Z-]+)     # first name (can include hyphen but not space)
    [._]                         # dot or underscore character
    (?P<last>[0-9a-zA-Z-]+)      # last name (can include hyphen but not space)
    @                            # @ symbol
    .*                           # any other crap
    """,
    re.UNICODE | re.VERBOSE)