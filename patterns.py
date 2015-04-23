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
    # looks for lastname, firstname [other stuff] 
    # handles names with hyphens or spaces
    # must have comma (lastname, firstname)
    # \"                        # double quote (must be escaped in re.VERBOSE mode)
    r"""
    [\"\']?                   # optional leading single or double quote
    (?P<last>[\w\s\-\']+)     # last name (can include space or hyphen)
    \,                        # comma separator
    \s{1,2}                   # one or two spaces
    (?P<first>[\w\s\-]+)      # first name (can include space or hyphen)
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_2 = re.compile(
    # looks for "firstname lastname [other stuff]" (between quotes)
    # handles names with hyphens or spaces
    # must NOT have comma (firstname [space] lastname)
    r"""
    \"                        # double quote (must be escaped in re.VERBOSE mode)
    (?P<first>[\w]+)          # first name (can include space or hyphen)
    \s{1,2}                   # one or two spaces
    (?P<last>[\w\']+)         # last name (can include space or hyphen)
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_3 = re.compile(
    # looks for firstname lastname <email@domain.tld> (no quotes)
    r"""
    [\"\']?                   # optional leading single or double quote
    (?P<first>[\w\s]+)        # first name (can include space or hyphen)
    \s{1,2}                   # one or two spaces
    (?P<last>[\w\s]+)         # last name (can include space or hyphen)
    \s{1,2}                   # one or two spaces
    [<(]                      # start of the email address (which we're ignoring)
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_4 = re.compile(
    # looks for firstname.lastname@domain.tld
    # where separator must exist and can be dot or underscore
    # only works when email is at the beginnng of the line (when matching)
    r"""
    [\"\']?                   # optional leading single or double quote
    (?P<first>[\w\-]+)     # first name (can include hyphen but not space)
    [._]                      # dot or underscore character
    (?P<last>[\w\-]+)      # last name (can include hyphen but not space)
    [1-4]?                    # optional trailing digit
    @                         # @ symbol
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)

pattern_names_5 = re.compile(
    # looks for firstname lastname [other stuff]
    r"""
    [\"\']?                   # optional quote char (must be escaped in re.VERBOSE mode)
    (?P<first>\w+)            # first name 
    \s{1,2}                   # one or two spaces
    (?P<last>\w+)             # last name
    \s{1,2}                   # one or two spaces
    .*                        # any other crap
    """,
    re.UNICODE | re.VERBOSE)


pattern_names_6 = re.compile(
    # looks for firstname lastname [other stuff], optionally with a middle initial
    r"""
    (?P<first>\w+)            # first name
    \s{1,2}                   # one or two spaces
    (?P<mi>\w\.\s{1,2})?      # optional middle initial period space
    (?P<last>[\w\'\-]+)       # last name
    """,
    re.UNICODE | re.VERBOSE)


pattern_names_7 = re.compile(
    # looks for first.i.last@domain.tld
    r"""
    (?P<first>[\w\-]+)         # first name
    \.                         # dot
    (?P<middle>\w+\.)          # middle, dot
    (?P<last>[\w\-]+)          # last name
    @                          # @ symbol
    .*                         # any other crap
    """,
    re.UNICODE | re.VERBOSE)


pattern_names_8 = re.compile(
    # Here we are searching within a string to find the email address containing a
    # dot or underscore which presumably separates first and last names
   r"""
    (?P<first>[\w\-]+)         # first name
    [\.\_]                     # dot or underscore
    (?P<middle>\w+\.)?         # optional middle, dot
    (?P<last>\w+)              # last name
    @                          # @ symbol
    .*                         # any other crap
    """,
    re.UNICODE | re.VERBOSE)

name_patterns = [
    pattern_names_1, 
    pattern_names_2, 
    pattern_names_3, 
    pattern_names_4, 
    pattern_names_5, 
    pattern_names_6,
    pattern_names_7,
    pattern_names_8,
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
