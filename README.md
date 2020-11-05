# Relationship Grapher

## Introduction:
This tool will take an Excelfile as input and generate a diagram as output, depicting the relationships between different entities.

## Usage:
To use this tool, you can need to run:

    python RelationshipGrapher.py -h

This will show you the possible parameters. For a simple sample you can use:

    python RelationshipGrapher.py -c -x Relations.xlsx

Replace the Relations.xlsx with the full path to your Excel file.

You can also just double click on it in Windows, provided that you:
Put the Excel file with the name Relations.xlsx in the same folder as the Executable 

## Requirements:
1. Python 3
2. Excel file (Very specific format. See included file)
3. Some python libraries (see Installation)
4. Internet access to http://www.plantuml.com/plantuml/img/ or alternatively, a local PlantUML server

## Installation:
1. Install Python (Only tested on Python version 3.7)
2. Install the following libraries for Python (I use a separate virtual environment for this):

	```pip install pandas numpy xlrd plantuml Pillow```

## Conclusion:
Proudly developed for myself :) 

Enjoy!
