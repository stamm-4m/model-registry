""" fairds_ontology.py

    PURPOSE:
        Helper class for the metadata ontology

    REQUIREMENTS:
        os, re, json, copy, pandas as pd, from openpyxl import load_workbook
    
    EXAMPLES:

        #---------------------
        # EXAMPLE 1: load excel file

            fds = fairds_ontology()
            fds.load_from_excel()
            
        
        
        #---------------------
        # EXAMPLE 2: convert excel to tsv

            fds = fairds_ontology()
            fds.load_from_excel()
            fds.convert_to_tsv()

        
        #---------------------
        # EXAMPLE 3: Load from tsv files

            fds = fairds_ontology()
            fds.load_from_tsv()
            fds.pretty_print(fds.terms)
            print(fds.terms['Preferred unit'])

        
        #---------------------
        # EXAMPLE 4: Put all the terms and units into a dict, set
        
            fds = fairds_ontology()
            fds.load_from_excel()
            fds.get_all_terms()


        #---------------------
        # EXAMPLE 5: Print out the set of terms
        
            fds = fairds_ontology()
            fds.load_from_excel()
            fds.get_all_terms()
            print(fds.terms_all)
        

        #---------------------
        # EXAMPLE 6: Print out the set of units
        
            fds = fairds_ontology()
            fds.load_from_excel()
            fds.get_all_terms()     
            print(fds.terms_units)

        

        #---------------------
        # EXAMPLE 7: Print out a term from a single key
        
            fds = fairds_ontology()
            fds.load_from_excel()
            fds.get_all_terms()     
            print(fds.terms['Item label'])

        

        #---------------------
        # EXAMPLE 8: Print out a units 
        
            fds = fairds_ontology()
            fds.load_from_excel()
            fds.get_all_terms()     
            print(fds.terms_units_dict)

            print('\n\n')
            print(fds.terms_units_dict.keys())
            
            print('\n\n')
            print(fds.terms_units_dict['ºC'])

            print('\n\n')  
            fds.query_term_units(query_='%')

         

        #---------------------
        # EXAMPLE 9: Print out top 100 rows of a particular hierarchy

            fds = fairds_ontology()
            fds.load_from_excel()
            print(fds.observationunit.head(100))

        
        #---------------------
        # EXAMPLE 10: Print out a units 
        
            fds = fairds_ontology()
            fds.load_from_excel()
            fds.get_all_terms()    
            print(fds.observationunit.head(100))
            fds.set_terms()
            print(fds.observationunit.head(100))
            fds.save_excel()


"""
#-----------------------
# PACKAGES
#-----------------------
import os
import re
import json
import copy
import pandas as pd
from openpyxl import load_workbook


#-----------------------
# VARIABLES
#-----------------------



#-----------------------
# FUNCTIONS
#-----------------------
def check_labels(term_fname: str = "terms.tsv", separator_: str = '\t', term_file_label_index: int = 0,
                 metadata_fnames: list = ["Assay.tsv", "Investigation.tsv", "ObservationUnit.tsv", "Sample.tsv", "Study.tsv"], 
                 metadata_file_label_index: int = 2) -> None:
    """ check_labels: Check the labels
            
        INPUT:
            term_fname              = Filename of the term file (str, default = "terms.tsv")  
            separator_              = Separator of the file (str, default = '\t')
            term_file_label_index   = The column index of 'label' in the terms file (int, default = 0)
            metadata_fnames         = Metadata filenames (list, default = ["Assay.tsv", "Investigation.tsv", "ObservationUnit.tsv", "Sample.tsv", "Study.tsv"]) 
            metadata_file_label_index = The column index of 'label' in the metadata files (int, default = 2)

        OUTPUT:
            None
            
    """
    print("Checking that all item labels in the data files are present in terms.tsv")

    item_labels = set()

    with open(term_fname, "r") as term_file:

        #item_label_index = 0 #term_file.next().split("\t").index("Item label")

        for line in term_file:

            item_labels.add(line.split(separator_)[term_file_label_index].lower())
            
    for metadata_file in metadata_fnames:

        with open(metadata_file, "r") as read_file:

            #item_label_index = 2 #read_file.next().split("\t").index("Item label")
                
            for line in read_file:

                item = line.split(separator_)[metadata_file_label_index].lower()
                
                assert item in item_labels
        
    print("All item labels in the data files are present in terms.tsv")



#-----------------------
# CLASSES
#-----------------------
class fairds_ontology:

    def __init__(self, 
                 sheet_names: list = ['regex', 'terms', 'Investigation', 'Study', 'ObservationUnit', 'Sample', 'Assay'],
                 level_sheet_headers: list = ["Level","Package name","Item label","Requirement","value syntax",	"example"],
                 regex_sheet_headers: list = ["short hand form","long form","example name","description"],
                 terms_sheet_headers: list = ["Item label","Value syntax","Example","Preferred unit","URL","Definition"],
                 fairds_ontology_xls_filename: str = "metadata.xlsx") -> None:
        """ init: Initialise class

                INPUT:
                    sheet_names = sheet names for the various terms
                            default: ['regex', 'terms', 'Investigation', 'Study', 'ObservationUnit', 'Sample', 'Assay'] (list)
                    terms_sheet_headers = the headers for each sheet
                            default: ["Level",	"Package name",	"Item label",	"Requirement",	"value syntax",	"example"] (list)
                    fairds_ontology_xls_filename = FAIR Data Station Ontology excel filename
                            default: "metadata.xlsx" (str)
                    
                OUTPUT:
                    None, initialise class

        """
        #---------------------
        # VARIABLES
        #---------------------
        self.metadata_filepath: str = fairds_ontology_xls_filename
        self.metadata_filepath_tmp: str = "metadata_tmp.xlsx"

        self.sheet_names: list = []
        self.level_sheet_headers: list = level_sheet_headers
        self.terms_sheet_headers: list = terms_sheet_headers
        self.regex_sheet_headers: list = regex_sheet_headers
        self.sheetnames: list = sheet_names
        self.tsv_files: list = []

        #-----------------
        # dataframes
        self.regex = None
        self.terms = None 
        self.investigation = None
        self.study = None
        self.observationunit = None
        self.sample = None
        self.assay = None

        #-----------------
        # all terms
        self.terms_all: set = set()
        self.terms_units: set = set()
        self.terms_dict: dict = dict()
        self.terms_units_dict: dict = dict()

        #------------------
        # regex dict
        self.regex_dict: dict = dict()



        #---------------------
        # Functions
        #---------------------
        self.generate_tsv_filenames()

    

    #-----------------------
    # GENERIC FUNCS
    #-----------------------
    def pretty_print(self, df, rows_to_show: int = 100) -> None:
        """ pretty_print: 

                INPUT:
                    df = dataframe
                    rows_to_show = number of rows to show (default: 100)

                OUTPUT:
                    None, print dataframe
        
        """
        print(df.head(rows_to_show))
        #print(df['Level'])



    def export_dict(self, dict_to_export: dict) -> None:
        """ export_dict: Export a dict to json
            
            INPUT:
                dict_to_export: dictionary to export

            OUTPUT:
                None, export dict

        """
        #----------------------
        # Lets make a copy to avoid modifying the dict
        dict_to_export = copy.deepcopy(dict_to_export)

        #----------------------
        # Replace nan with None so the json is correct
        self.replace_nan_in_dict(dict_to_check=dict_to_export)

        #----------------------
        # Make the json dump
        json.dump( dict_to_export, 
                  open( "terms_dict.json", 'w' ), 
                  indent=4)


    def replace_nan_in_dict(self, dict_to_check: dict, replace_nan_with = None) -> None:
        """ check_nan_in_dict: 
        
            INPUT: 
                dict_to_check: Description
                replace_nan_with: Description

            OUTPUT:
                None, replaces NaN in dict
        """

        for key_i in dict_to_check:

            if isinstance(dict_to_check[key_i], dict):

                for key__ii in dict_to_check[key_i]:

                    if isinstance(dict_to_check[key_i][key__ii], dict):

                        for key___iii in dict_to_check[key_i][key__ii]:

                            if pd.isna(dict_to_check[key_i][key__ii][key___iii]):
                                dict_to_check[key_i][key__ii][key___iii] = replace_nan_with
                    
                    else:
                        if isinstance(dict_to_check[key_i][key__ii], list):
                            pass
                        else:
                            if pd.isna(dict_to_check[key_i][key__ii]):
                                dict_to_check[key_i][key__ii] = replace_nan_with                        
                    
            else:
                if isinstance(dict_to_check[key_i], list):
                    pass
                else:
                    if pd.isna(dict_to_check[key_i]):
                        dict_to_check[key_i] = replace_nan_with   

    #-----------------------
    # SPECIFIC FUNCS
    #-----------------------
    def generate_tsv_filenames(self, file_extension: str = '.tsv') -> None:
        """ generate_tsv_filenames: Generate tsv filenames

            INPUT:
                file_extension = file extension of tsv files, default: '.tsv'

            OUTPUT:
                None, append to self.tsv_files
        
        
        """
        for filename_ in self.sheetnames:

            self.tsv_files.append(filename_ + file_extension)



    def load_from_tsv(self, separator_ = '\t') -> None:
        """ load_from_tsv: Load from a tsv file

                INPUT:
                    seperator_ = separator 

                OUTPUT:
                    None
            
        """

        self.regex = pd.read_csv("regex.tsv", sep=separator_)
        self.terms = pd.read_csv("terms.tsv", sep=separator_)
        self.investigation = pd.read_csv("Investigation.tsv", sep=separator_)
        self.study = pd.read_csv("Study.tsv", sep=separator_)
        self.observationunit = pd.read_csv("ObservationUnit.tsv", sep=separator_)
        self.sample = pd.read_csv("Sample.tsv", sep=separator_)
        self.assay = pd.read_csv("Assay.tsv", sep=separator_)



    def load_from_excel(self) -> None:
        """ load_from_excel: Load from an excel file

                INPUT:
                    None

                OUTPUT:
                    None       
                
        """
        with pd.ExcelFile(self.metadata_filepath) as xls:  

            self.regex = pd.read_excel(xls, "regex", names = self.regex_sheet_headers) 
            self.terms = pd.read_excel(xls, "terms", names = self.terms_sheet_headers) 
            self.investigation = pd.read_excel(xls, "Investigation", names = self.level_sheet_headers) 
            self.study = pd.read_excel(xls, "Study", names = self.level_sheet_headers) 
            self.observationunit = pd.read_excel(xls, "ObservationUnit", names = self.level_sheet_headers) 
            self.sample = pd.read_excel(xls, "Sample", names = self.level_sheet_headers) 
            self.assay = pd.read_excel(xls, "Assay", names = self.level_sheet_headers) 



    def convert_to_excel(self)-> None:
        """ convert_to_excel: Convert tsv files to excel files

            INPUT:
                None

            OUTPUT:
                None
        
        """
        #-------------------
        # Load all TSV files in the current directory into a dictionary of pandas DataFrames
        #~tsv_files = ['regex.tsv', 'terms.tsv', 'Investigation.tsv', 'Study.tsv', 'ObservationUnit.tsv', 'Sample.tsv', 'Assay.tsv']
        dataframes = {os.path.splitext(os.path.basename(file))[0]: pd.read_csv(file, sep='\t') for file in self.tsv_files}

        #-------------------
        # Create an Excel writer object
        writer = pd.ExcelWriter(self.metadata_filepath)

        #-------------------
        # Write each DataFrame to a separate sheet in the Excel file
        for sheet_name, df in dataframes.items():

            df.to_excel(writer, sheet_name=sheet_name, index=False)

        #-------------------
        # Save the Excel file
        writer.close()



    def convert_to_tsv(self, filename: str = "metadata.xlsx", 
                       header_row_idx: int = 1, 
                       data_row_idx: int = 2,
                       ) -> None:
        """ convert_to_tsv: Convert ontology file to tab delimited files

            INPUT:
                filename        = filename, default: "metadata.xlsx" (str)
                header_row_idx  = header row index, default: 1 (integer)
                data_row_idx    = data row starting index, default 2 (integer)
        
            OUTPUT:
                None

        """
        #------------------------
        # Load the Excel workbook
        wb = load_workbook(filename)

        #------------------------
        # Iterate through each sheet in the workbook
        for sheet_name in wb.sheetnames:

            ws = wb[sheet_name]
            
            # Extract headers from the first row
            headers = [cell.value for cell in ws[header_row_idx]]  # Assuming the first row contains the headers
            
            # Create a list to store the data
            data = []

            # Starting from the second row for data
            for row in ws.iter_rows(min_row=data_row_idx, values_only=False):  

                row_data = []

                for cell in row:

                    # Check if cell value is a boolean
                    if isinstance(cell.value, bool):  

                        # Keep the boolean value as-is or convert to string if needed
                        row_data.append(str(cell.value).lower())  # Or `row_data.append(str(cell.value))` for 'True'/'False'

                    elif cell.number_format in ['0%', '0.00%']:  # Check if cell format is percentage

                        if cell.value is not None:

                            # Convert to percentage string

                            row_data.append(f"{cell.value * 100:.2f}%")

                        else:

                            row_data.append(None)

                    else:

                        # Keep the original value for non-percentage cells
                        row_data.append(cell.value)

                data.append(row_data)
            
            #------------------------
            # Convert to a DataFrame
            df = pd.DataFrame(data, columns=headers)  # Use the headers for column names
            
            #------------------------
            # Export the sheet to a TSV file
            df.to_csv(f"{sheet_name}.tsv", sep="\t", index=False)



    def save_excel(self, filename) -> None:
        """ save_excel: Save the excel

            INPUT:
                filename = filename for file

            OUTPUT:
                None, creates metadata excel file with _tmp at end

        """
        with pd.ExcelWriter(filename) as writer:  
            
            self.regex.to_excel(writer,  sheet_name="regex") 
            self.terms.to_excel(writer,  sheet_name="terms") 
            self.investigation.to_excel(writer,  sheet_name="Investigation") 
            self.study.to_excel(writer,  sheet_name="Study") 
            self.observationunit.to_excel(writer,  sheet_name="ObservationUnit") 
            self.sample.to_excel(writer,  sheet_name="Sample") 
            self.assay.to_excel(writer,  sheet_name="Assay") 



    def get_all_terms(self, unit_sep = '|') -> None:
        """ get_all_terms: Get all terms
        
                INPUT:
                    unit_sep = separator for units column (default:|)

                OUTPUT:
                    None, modifies         
                          self.terms_all = set()
                          self.terms_units = set()
                          self.terms_dict = dict()
                          self.terms_units_dict = dict()

        """
        for idx, row in self.terms.iterrows():
            
            #---------------
            # Add labels to terms_all set
            if isinstance(row['Item label'], float):
                self.terms_all.add(row['Item label']) 

            else:
                self.terms_all.add(row['Item label'].lower()) 

            #----------------
            # Add units to terms_unit set
            if not isinstance(row['Preferred unit'], float):
                tmp_ = row['Preferred unit'].split(unit_sep)
            else:
                tmp_ = []
            
            if len(tmp_) >0:
                for item in tmp_:
                    self.terms_units.add(item)


            #------------------
            # Make a units dictionary
            if len(tmp_) >0:

                for item in tmp_:

                    if item in self.terms_units_dict:

                        self.terms_units_dict[item]['found at'].append(idx)
                        self.terms_units_dict[item]['Item label'].append(row['Item label'])
                    
                    else:

                        self.terms_units_dict[item] = {}
                        self.terms_units_dict[item]['Item label'] = [row['Item label']]
                        self.terms_units_dict[item]['found at'] = [idx]


            #------------------
            # Make a terms dictionary
            #------------------

            #--------------
            # check if label is not nan
            if not isinstance(row['Item label'], float):
                key_ = row['Item label'].lower()
            else:
                key_ = row['Item label']

            #--------------
            # check if key already in dict
            if key_ in self.terms_dict:
                
                print(f"\t\t Label: {key_} - Identical label at row {idx}")
                self.terms_dict[key_]['found at'].append(idx)
            
            else:

                #print(idx, '\t', key_)
                self.terms_dict[key_] = {}
                self.terms_dict[key_]['Item label'] = row['Item label']
                self.terms_dict[key_]['Value syntax'] = row['Value syntax']

                self.terms_dict[key_]['Example'] = row['Example']
                self.terms_dict[key_]['Preferred unit'] = row['Preferred unit']
                self.terms_dict[key_]['URL'] = row['URL']
                self.terms_dict[key_]['Definition'] = row['Definition']

                self.terms_dict[key_]['found at'] = [idx]



    def check_terms(self):
        """ check_terms: Check all terms exist

                REF:
                    Check empty set:
                    https://stackoverflow.com/questions/21191259/returning-boolean-if-set-is-empty

        """
        #------------------
        # Check if spreadsheets are loaded        
        for item in [self.regex,  self.terms,  self.investigation,  self.study,  self.observationunit, self.sample, self.assay]:
            if item is None:
                raise ValueError(f'{item} is missing ')
            
        #------------------
        # Call function if empty set
        if len(self.terms_all) == 0:
            self.get_all_terms()

        #------------------
        # Iterate over sheets
        for metadata_hierarchical_level in [self.investigation,  self.study,  self.observationunit, self.sample, self.assay]:
            
            for idx, row in metadata_hierarchical_level.iterrows():
                
                if isinstance(row['Item label'], float):

                    term = row['Item label']

                else:
                    term = row['Item label'].lower()
                
                assert term in self.terms_all, f"term missing from term sheet, got: {term} at row {idx}"       



    def query_term_units(self, query_: str = '', print_values: bool = True, return_value: bool = False):
        """ query_term_units: Query the units dict

            INPUT
                query_ = the query to the dictionary (default '')
                         note: 'keys', 'number of units' will trigger return keys and len
                                all other queries will trigger a 'get' func to dictionary

                print_values = whether to print the values of the query (default True) 
                return_value = whether to return the values of the query (default False)
            
            OUTPUT:
                if return_value:
                    either .keys(), len(keys()), or .get(key,{})
        

        """
        if query_ == 'keys':
            
            if print_values:

                for item in self.terms_units_dict.keys():

                    print(item)

            if return_value:

                return self.terms_units_dict.keys()
        
        elif query_ == 'number of units':

            if print_values:

                print(len(self.terms_units_dict.keys()))

            if return_value:   

                return len(self.terms_units_dict.keys())

        else:
            if print_values:

                print(self.terms_units_dict.get(query_, 'Key not found') )
            
            if return_value:  

                return self.terms_units_dict.get(query_, {}) 



    def set_terms(self, make_old_metadata_tmpfile = True) -> None:
        """ set_terms: Set terms

            INPUT:
                make_old_metadata_tmpfile = make an excel file (self.metadata_filepath_tmp) to store original values

            OUTPUT:
                None
        
        """
        #-------------------
        # Make a copy of the metadata excel
        if make_old_metadata_tmpfile:
            self.save_excel(filename = self.metadata_filepath_tmp)

        #-------------------
        # Set terms
        for dataframe_item in [self.investigation, self.study, self.observationunit, self.sample, self.assay]: 

            for idx, row in dataframe_item.iterrows():

                if not isinstance(row['Item label'], float):

                    key_ = row['Item label'].lower()

                else:

                    key_ = row['Item label']

                
                found_key = self.terms_dict.get(key_, None) 


                if found_key is not None:
                
                    if pd.isna(row['value syntax']):
                        dataframe_item.loc[idx,'value syntax'] = found_key['Value syntax']
                        print(f'\t Changed {key_} value syntax to {found_key['Value syntax']}')

                    if pd.isna(row['value syntax']):
                        dataframe_item.loc[idx,'example'] = found_key['Example']
                        print(f'\t Changed {key_} example to {found_key['Example']}')

                else:
                    print(f'{key_} missing value')



    def make_terms_md(self, url_ignores: list = ["w3id.org"]) -> None:
        """ make_terms_md: Make markdown file for terms

            INPUT:
                url_ignores = url to ignore (list, default = ["w3id.org"])

            OUTPUT:
                None, creates markdown files per term

            Note: 
                # Item label	Value syntax	Example	Preferred unit	URL	Definition
                label, syntax, example, unit, url, definition = line.split("\t")

        """
        print('Generating markdown files...')

        #------------------
        # Call function if empty set
        if len(self.terms_all) == 0:
            self.get_all_terms()

        #------------------
        # Loop through term keys
        for key_ in self.terms_dict:
            if not pd.isna(self.terms_dict[key_]['Item label']):
                print(f'\t Making {key_}: markdown file')            

                #------------------
                # Get variables
                label   = self.terms_dict[key_]['Item label']
                syntax= self.terms_dict[key_]['Value syntax']
                example= self.terms_dict[key_]['Example']
                unit= self.terms_dict[key_]['Preferred unit']
                url= self.terms_dict[key_]['URL']
                definition = self.terms_dict[key_]['Definition']

                #-------------------
                # Change nan values
                if pd.isna(url):
                    url = ''

                if pd.isna(syntax):
                    syntax = ''

                if pd.isna(example):
                    example = ''

                if pd.isna(unit):
                    unit = ''

                if pd.isna(definition):
                    definition = ''


                #---------------------
                # Perform actions...          

                ignore = False

                for url_ignore in url_ignores:
                    print(url_ignore)

                    if url_ignore in url:

                        ignore = True
                        break
                    
                if ignore: continue

                if len(url) == 0:

                    url_label = label.replace(" ", "_").lower().replace("/", "_")

                    #------------------
                    # Turn into a markdown file using the markdown library
                    markdown = f"""
                                    # Term: {label}
                                        
                                    {definition}

                                    |              |                                    |
                                    |------------------|-----------------------------------------|
                                    | Syntax          | `{syntax}`                              |
                                    | Example         | `{example}`                             |
                                    | Unit            | `{unit}`                                |
                                    | URL             | [fairds:{url_label}](http://fairbydesign.nl/ontology/{url_label}) |

                                    """
                    
                    #------------------
                    # Removing rows that have empty values
                    for m in markdown.split("\n"): 
                        if "``" in m: 
                            markdown = markdown.replace(m + "\n", "")
                            print(markdown)
                    
                    #------------------
                    # Remove _
                    label = label.replace(" ", "_").lower().replace("/", "_")
                    label = label.replace("?", "")

                    #------------------
                    # Save markdown term file
                    with open(f"ontology/docs/{label}.md", "w") as file_md:
                        try:
                            file_md.write(markdown)
                        except:
                            print(f'\t {key_} Error in encoding')

                    #------------------
                    # Notify users
                    print(f"Created {label}.md")



    def make_ontology_dir(self) -> None:
        """ make_ontology_dir: Make ontology directory
        
            INPUT:
                None

            OUTPUT:
                None, create ontology directory
                      create ontology/docs directory

        """
        if not os.path.exists("ontology"):
            os.mkdir("ontology")
            print("Created ontology folder")

        if not os.path.exists("ontology/docs"):
            os.mkdir("ontology/docs")
            print("Created ontology/docs folder")



    def check_example_regex_match(self)->None:
        """ check_example_regex_match: Check if the regex of examples matches
        
            REF:
                https://docs.python.org/3/library/re.html#regular-expression-syntax
                https://stackoverflow.com/questions/12595051/check-if-string-matches-pattern

        """
        #----------------------
        #
        missing_syntax = 0
        missing_syntax_in_regex = 0
        missing_example = 0
        not_matching = 0
        term_counter = 0


        #----------------------
        # REGEX
        self.regex_dict = self.regex.to_dict('index')

        print(self.regex_dict)


        #----------------------
        # Loop through dict
        for term_ in self.terms_dict.keys():

            term_counter += 1

            example_ = self.terms_dict[term_]['Example']
            syntax_ = self.terms_dict[term_]['Value syntax']
            #print(f'Checking {term_} with example -{example_}- and syntax -{syntax_}-')

            try:

                syntax_to_test = self.regex_dict[syntax_]['short hand form']

            except:

                print(f'\t {term_}: regex not in regex.tsv {syntax_}')

                missing_syntax += 1

                if pd.isna(syntax_):

                    missing_syntax_in_regex +=1

                    continue

                else:

                    syntax_to_test = syntax_
                

            #print(term_, example_, syntax_, syntax_to_test)

            if pd.isna(example_):
                
                print(f'\t {term_}: missing example')
                missing_example += 1
            
            else:

                if re.search(str(example_), syntax_to_test):
                    #print(f'\t {term_}: example matches')
                    pass
                    
                else:
                    print(f'\t {term_}: example {example_} does not match syntax {syntax_to_test}')
                    not_matching +=1
        
        print(f'\n\n Stats: \n\t Number of missing syntax in regex: {missing_syntax_in_regex} / {term_counter} \n\t Number of missing syntax: {missing_syntax} / {term_counter} \n\t Number of missing examples: {missing_example} / {term_counter} \n\t Number of not matching examples: {not_matching} / {term_counter}')



if __name__ == "__main__":
        
    fds = fairds_ontology()
    fds.load_from_excel()
    fds.get_all_terms()    

    #fds.export_dict(fds.terms_dict)

    #print(fds.observationunit.head(100))
    #fds.set_terms()
    #print(fds.observationunit.head(100))
    #fds.save_excel(fds.metadata_filepath)
    #fds.check_terms()

    #fds.make_terms_md()


    fds.check_example_regex_match()
