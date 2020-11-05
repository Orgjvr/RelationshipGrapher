#pip install pandas numpy xlrd plantuml Pillow
import pandas as pd
import numpy as np
import sys
import plantuml #https://github.com/dougn/python-plantuml
import os
import argparse 
import warnings

from PIL import Image


# Globals
global UsedEntities_df
global Entities
global MaxLevel


def exitGrapher(code, message="NONE"):
    #This is to exit with a non zero status
    if message != "NONE":
        print(message)    
    sys.exit(code)


def init_argparse() -> argparse.ArgumentParser:
    appVersion="0.6.3"
    appDescription="Generate a picture depicting relationships between entities."
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] ...",
        description=appDescription
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version "+appVersion
    )
    parser.add_argument('-c', '--createcopy', action='store_true', help="Create a copy of input file and work with copy")
    parser.add_argument('-cf','--copyFileName', default="temp.xlsx", help="Filename for copy created by the -c option.")
    parser.add_argument('-x', '--excelfile', default="Relations.xlsx", help="Specify the name of the input Excel file")
    parser.add_argument('-d', '--debug', action='store_true', help="Shows debugging output")
    parser.add_argument('-t', '--type', dest='inputType', type = str.lower, choices=['excel', 'csv'], default="excel",
                    help="Specify the type of input file(s)")
    parser.add_argument('-lm','--LimitMaxLevel', type = int, default=0, help="Limit generation by specifying a MAX level of depth.")
    parser.add_argument('-o', '--outputfile', default="output.png", help="Specify the name of the output file")
    parser.add_argument('-s', '--server', default="http://www.plantuml.com/plantuml/img/", help="Specify the URL of the server to use.")
    #parser.add_argument('files', nargs='*')
    return parser

def main(args): # -> None:
    # Globals
    global UsedEntities_df
    global Entities
    global MaxLevel

    if args.debug:
        print("args:",args)    


    if (args.inputType == "excel"):
        InputFile=args.excelfile
    else:
        print("ERROR: Currently only Excel input are allowed.")    
        exitGrapher(1)

    OutputFile=args.outputfile

    EntitiesHDR=0
    RelationsHDR=0
    TypesHDR=0
    scale="scale max 1800 width"
    #MaxLevel=0
    MaxLevel=args.LimitMaxLevel

    if (args.createcopy):
        # We make a copy of the file to ensure we have access to it.
        command="echo F|xcopy /Q /Y /F  \""+InputFile+"\" \""+args.copyFileName+"\""
        if args.debug:
            print('command:',command)
        result=os.system(command)
        if args.debug:
            print('result:',result)
        InputFile=args.copyFileName




    Entities=""
    Dependencies=""
    containerList=[]
    prioritisedContainers=[]

    # define Python user-defined exceptions
    class Error(Exception):
        """Base class for other exceptions"""
        pass

    class CircularReferenceError(Error):
        """Raised when a circular reference has been detected"""
        pass

    def populateChildren(prioritisedEntities, currentEntity, currentLevel):
        """This is a recursive function
        to populate the list with the children of a container"""
        global MaxLevel
        global UsedEntities_df
        if (MaxLevel == 0 or MaxLevel > currentLevel):
            currentLevel=currentLevel+1
            # First populate current Entity in list of prioritised entities
            if args.debug:
                print('currentEntity: ',currentEntity)
                #print('Level', currentLevel, ' - currentEntityName: ',currentEntity[1]['EntityName'])
            prioritisedEntities = prioritisedEntities.append({'EntityName' : currentEntity[1]['EntityName'], 'Type' : currentEntity[1]['Type'], 'Container': currentEntity[1]['Container'], 'Description' : currentEntity[1]['Description'], 'OptionalDescription' : currentEntity[1]['OptionalDescription'], 'ShowOptional' : currentEntity[1]['ShowOptional'], 'Level' : currentLevel } , ignore_index=True)
            # Also populate current Entity in Entities string for UML
            global Entities
            Entities=Entities+"state " + currentEntity[1]['EntityName']
            if (pd.notna(currentEntity[1]['Type'])):
                Entities=Entities+"<<"+currentEntity[1]['Type']+">>"
            Entities=Entities+" { \n"
            if (pd.notna(currentEntity[1]['Description'])):
                Entities=Entities+currentEntity[1]['EntityName']+" : "+currentEntity[1]['Description']+"\n"
            if (pd.notna(currentEntity[1]['ShowOptional'])):
                showOptional = (currentEntity[1]['ShowOptional'] != "N")
            else:
                showOptional = True
            if (showOptional and pd.notna(currentEntity[1]['OptionalDescription'])):
                Entities=Entities+currentEntity[1]['EntityName']+" : "+currentEntity[1]['OptionalDescription']+"\n"
        
            # Get list of children and loop through them
            currentEntityName = currentEntity[1]['EntityName']
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=FutureWarning)
                childEntities = (UsedEntities_df.loc[UsedEntities_df['Container'] == currentEntityName])
            if args.debug:
                print('Level', currentLevel, ' - childEntities: ',childEntities)
            # Only add children if needed
            for childEntity in childEntities.iterrows():
                prioritisedEntities = populateChildren(prioritisedEntities, childEntity, currentLevel)	
            Entities=Entities+"}\n"
        else:
            if args.debug:
                print("INFO: Not adding children below level ",currentLevel)
        return prioritisedEntities   


    skinparam="skinparam state { \n"
    legend="state Legend { \n"

    # ToDo: Add options to load from CSV file or from database.
    try:
        excel_types_df = pd.read_excel(InputFile, sheet_name='Types', header=TypesHDR, usecols=['Type', 'Description', 'HTML_Color'], engine = 'xlrd')
    except ValueError as e:
        print("ERROR: Reading the TYPE definitions failed: ", e)
        exitGrapher(2)
    except PermissionError as e: 
        print("ERROR: ", e)
        print("Maybe try the -c option to make a copy.")
        exitGrapher(3)
    try:
        excel_entities_df = pd.read_excel(InputFile, sheet_name='Entities', header=EntitiesHDR, usecols=['EntityName', 'Type', 'Container', 'Description', 'OptionalDescription', 'ShowOptional', 'Special'])
    except ValueError as e:
        print("ERROR: Reading the ENTITY definitions failed: ", e)
        exitGrapher(4)
    except PermissionError as e: 
        print("ERROR: ", e)
        print("Maybe try the -c option to make a copy.")
        exitGrapher(5)
    try:
        excel_dependencies_df = pd.read_excel(InputFile, sheet_name='Relationships', header=RelationsHDR, usecols=['Entity', 'Dependency', 'Description'])
    except ValueError as e:
        print("ERROR: Reading the RELATIONSHIP definitions failed: ", e)
        exitGrapher(6)
    except PermissionError as e: 
        print("ERROR: ", e)
        print("Maybe try the -c option to make a copy.")
        exitGrapher(7)


    #Step 1: Get list of all types (First from types used by Entities and then properties defined by Types sheet)
    UsedTypes = pd.DataFrame(excel_entities_df)['Type'].dropna().unique().tolist()
    if args.debug:
        print("Typelist: ",UsedTypes)
    DefinedTypes = pd.DataFrame(excel_types_df)['Type'].dropna().str.strip().unique().tolist()
    for usedType in UsedTypes:
        for index, row  in excel_types_df.loc[excel_types_df['Type'] == usedType].iterrows():
            #Add type to skinparam
            skinparam=skinparam+"   backgroundColor<<"+row['Type']+">> "+row['HTML_Color']+" \n"
            #Add type to legend
            legend=legend+"state "+row['Type']+"<<"+row['Type']+">> { \n" + "     "+row['Type']+" : "+row['Description']+"\n   } \n"
    #Finally add closing part of skinparam and legend
    skinparam=skinparam+"} \n"
    legend=legend+"state Undefined { \n     Undefined: This type is not defined \n   } \n}"


    #Step 2:
    #containerList = pd.DataFrame(excel_entities_df)['Container'].dropna().str.strip().unique().tolist()

    #Step 3:
    # Build list of Entities without containers. This will be our driver for outside loop
    # For each entity build a list of dependant entities and loop through - Do recursively
    # Add check for circular reference
    UsedEntities_df = excel_entities_df.loc[excel_entities_df['EntityName'].notnull()]
    if ( len(UsedEntities_df.index) == 0 ):
        print("ERROR: No Entities defined. Define at least the starting Entity.")
        exitGrapher(8)

    # Add the containers to the UsedEntities_df if not there already.
    UsedContainers = pd.DataFrame(excel_entities_df)['Container'].dropna().unique().tolist()
    for container in UsedContainers:
        if args.debug:
            print("container: ",container)
        #if ( excel_entities_df.loc[excel_entities_df['EntityName'] == container ].count() == 0): #Check if container is defined as entity. If not add it.
        if ( ( excel_entities_df.loc[excel_entities_df['EntityName'] == container ]).empty ): #Check if container is defined as entity. If not add it.
            # Add the container to the UsedEntities_df
            if args.debug:
                print("Adding container: ",container)   
            UsedEntities_df = UsedEntities_df.append({'EntityName' : container, 'Type' : pd.NA, 'Container': pd.NA, 'Description' : pd.NA, 'OptionalDescription' : pd.NA, 'ShowOptional' : pd.NA, 'Special' : pd.NA } , ignore_index=True)
            
    if args.debug:
        print("UsedEntities: ",UsedEntities_df)
    topLevelEntities = UsedEntities_df.loc[UsedEntities_df['Container'].isnull()]
    #UsedEntities = pd.DataFrame(excel_entities_df)['EntityName'].dropna().str.strip().unique().tolist()
    if args.debug:
        print("topLevelEntities: ",topLevelEntities)    

    prioritisedEntities=pd.DataFrame(columns=['EntityName', 'Type', 'Container', 'Description', 'OptionalDescription', 'ShowOptional', 'Level'])
    # ToDo: Filter by entity/entities must be done in this next loop
    for Entity in topLevelEntities.iterrows():
        #print("usedEntity: ",usedEntity)
        prioritisedEntities = populateChildren(prioritisedEntities, Entity, 0)
        #for index, curEntity in excel_entities_df.loc[excel_entities_df['Container'].isnull()].iterrows():
        #    print("curEntity: ",curEntity)
    if args.debug:
        print("prioritisedEntities:",prioritisedEntities)
    # Step 4: Now add the dependencies
    # ToDo: Only add dependencies as needed.
    UsedDependencies_df = excel_dependencies_df.loc[excel_dependencies_df['Entity'].notnull()]
    for index, Dependency in UsedDependencies_df.iterrows():
        # Only add dependency to output if either entity or dependency is in prioritisedEntities
        if ( ( not ( prioritisedEntities.loc[prioritisedEntities['EntityName'] == Dependency['Entity'] ]).empty ) or ( not ( prioritisedEntities.loc[prioritisedEntities['EntityName'] == Dependency['Dependency'] ]).empty ) ) :
            if args.debug:
                print("test:",Dependency['Entity'])
            if (pd.isna(Dependency['Dependency'])):
                Dependencies=Dependencies+"[*]"
            else:
                Dependencies=Dependencies+Dependency['Dependency']
            
            Dependencies=Dependencies+" --> "+Dependency['Entity']
            if (pd.notna(Dependency['Description'])):
                Dependencies=Dependencies+" : "+Dependency['Description']
            Dependencies=Dependencies+"\n"



    try:
        plantUMLText=scale+"\n"+skinparam+"\n"+legend+"\n"+Entities+"\n"+Dependencies+"\n"
        #plantUMLText=scale+"\n"+skinparam+"\n"+Entities+"\n"+Dependencies+"\n"
        print('plantUMLText=<{}>'.format(plantUMLText))
        callPlantUML=plantuml.PlantUML(url=args.server)
        img=callPlantUML.processes(plantUMLText)
        f = open(OutputFile, "wb")
        f. write(img)
        f.close()
    except plantuml.PlantUMLConnectionError:
        print("ERROR: Error connecting or talking to PlantUML Server")
    except plantuml.PlantUMLHTTPError:
        print("ERROR: Request to PlantUML server returned HTTP Error.")
    except plantuml.PlantUMLError:
        print("ERROR: The generated code is incorrect")
    except:
        raise Exception



if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()
    main(args)
    img2 = Image.open(args.outputfile)
    img2.show()
    exitGrapher(0)    
