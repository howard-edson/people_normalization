# Overview
Given a list of people records consisting of a person's name and email address,
where each record can be in any of several common formats, this software
will find and parse the person's first and last names, and email address and domain
into separate columns in an output report. 

Additionally, it will perform [record linkage](http://en.wikipedia.org/wiki/Record_linkage), 
finding records that refer to the same real human person and placing them in the same
group. This is fuzzy logic and is intended to eliminate a large chunk of manual effort,
but does not entirely eliminate the need for human review.

The reocrd linkage algorithm is O(n^2), and has been tested on a laptop on input 
files of up to 20,000 records.

# Instructions
This program is run from the command line, as #>python run_process.py [filename].txt <enter>
It requires python and SQLAlchemy. It creates a SQLite database file called [filename].sqlite
and an output file called [filename]_output.txt, both in the same directory as the input file.

## The input file
The input file should be a two-column, tab-delimited ('\t') file with a header row. We use a tab
because from Excel you can save as type "unicode .txt". Unicode characters will work fine.
* Column 1 is person ID - the unique identifier for each person record from the source system
* Column 2 is the raw person record itself.

## The output file
We use a .txt extension for the output file because when you open this in Excel, the 
import wizard is invoked that walks the user through converting this tab-delimited report 
into an Excel file. First row contains field names.

# Technologies used
* Python
* Regular expression pattern matching
* SQLite - a popular embedded, ACID-compliant, serverless SQL database
* SQLAlchemy - an object-relational mapper
