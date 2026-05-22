""" model2seek.py

        Add and investigate models in a FAIRDOM-SEEK instance

        
        AUTHOR:
            Brett Metcalfe (0000-0002-5873-9815)
            Laboratory of Systems and Synthetic Biology, Wageningen University & Research, 
            Wageningen, The Netherlands


        FUNDED BY:
            The authors disclose receipt of the following financial support for the research,
            authorship, and publication of this article: European Union's Horizon 2020 research 
            and innovation programme projects ‘RI services to promote deep digitalization of 
            Industrial Biotechnology - towards smart biomanufacturing’ (BIOINDUSTRY 4.0, grant 
            agreement n° 101094287 [https://doi.org/10.3030/101094287]).

        
        REQUIREMENTS:
            yaml
            requests
            json
            os
            getpass

            
        CONTAINS:
            var:
                None

            func:
                None

            classes:
                model2seek


"""
#------------------------------
#       PACKAGES
#------------------------------
import yaml
import requests
import json
import os
import getpass


#------------------------------
#       VARIABLES
#------------------------------


#------------------------------
#       FUNCTIONS
#------------------------------


#------------------------------
#       CLASSES
#------------------------------
class model2seek:

    def __init__(self, 
                 base_url: str, 
                 token: str = None,

                ) -> None:
        """ init: Initialise class
        
                REF:
                    access policy = https://ibisbahub.eu/api#section/Policy
                    license = https://ibisbahub.eu/api#section/License
        
        
        """

        #-----------------------
        # FAIRDOM-SEEK Variables
        self.access_policy_: dict = {
                                    'no_access' : {'name': 'no_access', 'description': 'No access'},
                                    'view' : {'name': 'view', 'description': 'View only'},
                                    'download' : {'name': 'download', 'description': 'View and download'},
                                    'edit' : {'name': 'edit', 'description': 'View, download, and edit'}, 
                                    'manage' : {'name': 'manage', 'description': 'View, download, edit, and manage'},
                                    }
        
        #--------------------------
        # See: https://en.wikipedia.org/wiki/Media_type
        self.license_: dict = {

                            'CC0-1.0' : {'name': 'CC0-1.0', 'description' : 'CC0 1.0'},
                            'CC-BY-4.0' : {'name': 'CC-BY-4.0', 'description' : 'Creative Commons Attribution 4.0'},
                            'CC-BY-SA-4.0' : {'name': 'CC-BY-SA-4.0', 'description' : 'Creative Commons Attribution Share-Alike 4.0'},
                            'ODC-BY-1.0' : {'name': 'ODC-BY-1.0', 'description' : 'Open Data Commons Attribution License 1.0'},
                            'ODbL-1.0' : {'name': 'ODbL-1.0', 'description' : 'Open Data Commons Open Database License 1.0'},
                            'ODC-PDDL-1.0': {'name': 'ODC-PDDL-1.0', 'description' : 'Open Data Commons Public Domain Dedication and Licence 1.0'},
                            'notspecified' : {'name': 'notspecified', 'description' : 'License Not Specified'},
                            'other-at' : {'name': 'other-at', 'description' : 'Other (Attribution)'},
                            'other-open' : {'name': 'other-open', 'description' : 'Other (Open)'},
                            'other-pd' : {'name': 'other-pd', 'description' : 'Other (Public Domain)'},
                            'AFL-3.0' : {'name': 'AFL-3.0', 'description' : 'Academic Free License 3.0'},
                            'Against-DRM' : {'name': 'Against-DRM', 'description' : 'Against DRM'},
                            'CC-BY-NC-4.0' : {'name': 'CC-BY-NC-4.0', 'description' : 'Creative Commons Attribution-NonCommercial 4.0'},
                            'DSL' : {'name': 'DSL', 'description' : 'Design Science License'},
                            'FAL-1.3' : {'name': 'FAL-1.3', 'description' : 'Free Art License 1.3'},
                            'GFDL-1.3-no-cover-texts-no-invariant-sections' : {'name': 'GFDL-1.3-no-cover-texts-no-invariant-sections', 'description' : 'GNU Free Documentation License 1.3 with no cover texts and no invariant sections'},
                            'geogratis' : {'name': 'geogratis', 'description' : 'Geogratis'},
                            'hesa-withrights' : {'name': 'hesa-withrights', 'description' : 'Higher Education Statistics Agency Copyright with data.gov.uk rights'},
                            'localauth-withrights' : {'name': 'localauth-withrights', 'description' : 'Local Authority Copyright with data.gov.uk rights'},
                            'MirOS' : {'name': 'MirOS', 'description' : 'MirOS Licence'},
                            'NPOSL-3.0' : {'name': 'NPOSL-3.0', 'description' : 'Non-Profit Open Software License 3.0'},
                            'OGL-UK-1.0' : {'name': 'OGL-UK-1.0', 'description' : 'Open Government Licence 1.0 (United Kingdom)'},
                            'OGL-UK-2.0' : {'name': 'OGL-UK-2.0', 'description' : 'Open Government Licence 2.0 (United Kingdom)'},
                            'OGL-UK-3.0' : {'name': 'OGL-UK-3.0', 'description' : 'Open Government Licence 3.0 (United Kingdom)'},
                            'OGL-Canada-2.0' : {'name': 'OGL-Canada-2.0', 'description' : 'Open Government License 2.0 (Canada)'},
                            'OSL-3.0' : {'name': 'OSL-3.0', 'description' : 'Open Software License 3.0'},
                            'dli-model-use' : {'name': 'dli-model-use', 'description' : 'Statistics Canada: Data Liberation Initiative (DLI) - Model Data Use Licence'},
                            'Talis' : {'name': 'Talis', 'description' : 'Talis Community License'},
                            'ukclickusepsi' : {'name': 'ukclickusepsi', 'description' : 'UK Click Use PSI'},
                            'ukcrown-withrights' : {'name': 'ukcrown-withrights', 'description' : 'UK Crown Copyright with data.gov.uk rights'},
                            'ukpsi' : {'name': 'ukpsi', 'description' : 'UK PSI Public Sector Information'},

                            }
        
        self.media_types_ :dict = {
             

                        'application/json'          : {'type_': 'application/json', 'for': '.json'},
                        'application/ld+json'       : {'type_': 'application/ld+json', 'for': 'JSON-LD'},
                        'application/msword'        : {'type_': 'application/msword', 'for': '.doc'},
                        'application/pdf'           : {'type_': 'application/pdf', 'for': ' .pdf'},
                        'application/sql'           : {'type_': 'application/sql', 'for': '.sql'},   

                        'application/vnd.api+json'  : {'type_': 'application/vnd.api+json', 'for': 'vnd.api+json'},
                        'application/application/vnd.microsoft.portable-executable' : {'type_': 'application/application/vnd.microsoft.portable-executable',
                                                                                        'for': ['.efi', '.exe', '.dll']},
                        'application/vnd.ms-excel'      : {'type_': 'application/vnd.ms-excel', 'for': '.xls'},
                        'application/vnd.ms-powerpoint' : {'type_': 'application/vnd.ms-powerpoint', 'for': '.ppt'},    

                        'application/vnd.oasis.opendocument.text': {'type_': 'application/vnd.oasis.opendocument.text', 'for': '.odt'},
                        'application/vnd.openxmlformats-officedocument.presentationml.presentation': {'type_': 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'for': '.pptx'},
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'          : {'type_': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'for': '.xlsx'},
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'          : {'type_': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'for': '.docx'},
                        'application/x-www-form-urlencoded'          : {'type_': 'application/x-www-form-urlencoded', 'for': None},
                        'application/xml'          : {'type_': 'application/xml', 'for': '.xml'},
                        'application/zip'          : {'type_': 'application/zip', 'for': '.zip'},
                        'application/zstd'         : {'type_': 'application/zstd', 'for': '.zst'},


                        #-----------------------
                        # AUDIO:
                        'audio/mpeg'          : {'type_': 'audio/mpeg', 'for': '.mpeg'},
                        'audio/ogg'           : {'type_': 'audio/ogg', 'for': '.ogg'},


                        #-----------------------
                        # IMAGE:  
                        'image/avif'          : {'type_': 'image/avif', 'for': '.avif'},     
                        'image/jpeg'          : {'type_': 'image/avif', 'for': ['.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp']}, 
                        'image/png'           : {'type_': 'image/png', 'for': '.png'},     
                        'image/svg+xml'       : {'type_': 'image/svg+xml', 'for': '.svg'}, 
                        'image/tiff'           : {'type_': 'image/tiff', 'for': '.tif'},   


                        #-----------------------
                        # MODEL:  
                        'model/obj'          : {'type_': 'model/obj', 'for': '.obj'}, 


                        #-----------------------
                        # MULTIPART:  
                        ' multipart/form-data'          : {'type_': ' multipart/form-data', 'for': None}, 

                        #-----------------------
                        # TEXT:  
                        'text/plain'        : {'type_': 'text/plain', 'for': None}, 
                        'text/css'          : {'type_': 'text/css', 'for': '.css'}, 
                        'text/csv'          : {'type_': 'text/csv', 'for': '.csv'}, 
                        'text/html'         : {'type_': 'text/plain', 'for': '.html'}, 
                        'text/javascript'   : {'type_': 'text/javascript', 'for': '.js'}, 
                        'text/xml'          : {'type_': 'text/xml', 'for': None}, 


                        #-----------------------
                        # CODE:
                        'text/x-python'        : {'type_': 'text/x-python', 'for': '.py'},
                        'text/x-python3'        : {'type_': 'text/x-python3', 'for': '.py'},  
                        'application/x-python-code'        : {'type_': 'application/x-python-code', 'for': '.pyc'}, 
        }
        



        #-----------------------
        # FAIRDOM-SEEK Model variables
        #https://github.com/seek4science/seek/blob/event-types-and-hybrid-2413/config/default_data/model_formats.yml
        #https://github.com/seek4science/seek/blob/event-types-and-hybrid-2413/config/default_data/model_recommended_environments.yml
        #https://github.com/seek4science/seek/blob/event-types-and-hybrid-2413/config/default_data/model_types.yml
        self.SEEK_model_types: dict = {  }
        self.SEEK_model_types_list: list = []
        
        self.SEEK_model_formats: dict = {  }
        self.SEEK_model_formats_list: list = []
        
        self.SEEK_model_recommended_envs: dict = { }
        self.SEEK_model_recommended_envs_list: list = []

        self.load_seek_terms()


        #-----------------------
        # The possible file format for requests
        self.SEEK_model_json_file_formats: dict = {
                                                    '.pkl' : {'name': '.pkl', 'description': 'Python pickle file', 'format': ''},
                                                    '.py'  : {'name': '.py', 'description': 'Python file', 'format': ''},

                                            }

        #-----------------------
        # User defined variables
        self.filepath: str = ''
        self.metadata: dict = {}
        self.metadata_dump: str = '' 
        self.description: str = ''
        self.token_ : str = token
        self.session = None


        #----------------------
        # Required variables
        self.base_url = base_url
        #self.headers = {}
        


    def pretty_print_(self, dictionary_, indent_ = 4):
        """ pretty_print_: Pretty print dict
        
            INPUT:
                dictionary_ = dictionary to print
                indent_     = amount of indent, default : 4

            OUTPUT:
                None, printed dictionary

            REQUIREMENTS:
                import json
                
        """
        print('\n\n')
        print(json.dumps(
                            dictionary_,
                            #sort_keys   =True,
                            indent      =indent_,
                            #separators=(',', ': ')
                        )
                )
        print('\n\n')



    def start_session(self, 
                      headers_: dict = {
                                    "Content-type": "application/vnd.api+json",
                                    "Accept": "application/vnd.api+json",
                                    "Accept-Charset": "ISO-8859-1"
                                }  ) -> None:
        """ start_session: Start requests session
        
                INPUT:
                    headers_ = request header (dict, default: {
                                    "Content-type": "application/vnd.api+json",
                                    "Accept": "application/vnd.api+json",
                                    "Accept-Charset": "ISO-8859-1"
                                })

                OUTPUT:
                    None

        """
        self.session = requests.Session()
        
        if self.token_ is None:

            self.session.headers.update(headers_)
            self.session.auth = (input('Username:'), getpass.getpass('Password'))

        else:
            headers_["Authorization"] = 'Token ' + self.token_
            self.session.headers.update(headers_)
            



    def check_model_vars(self, 
                         containing_project_id : int,                  
                         model_creators: list[int] = [],
                         model_organisms: list[int] = [],):
        """ check_model_vars: Check the models variables

            INPUT:
                containing_project_id: int = the FAIRDOM-SEEK project ID
                model_creators: list[int] = the FAIRDOM-SEEK creator ID, has to be list of creators
                model_organisms: list[int]= the FAIRDOM-SEEK organism ID, has to be list of organisms

            OUTPUT:
                output_project : dict = dictionary of the project (keys: title, decription)
                output_creators : dict = dictionary of dictionaries the creators (keys: creator) 
                                        and (keys: first_name, last_name, orcid, name, description)
                output_organisms : dict = dictionary of dictionaries the organisms (keys: organisms) 
                                        and (keys: title, concept_uri, ontology_id, description)
                output_simple : list = simple list of output involving project, creators, and organisms
                                        prefaced by 'Project: ', 'Creator: ', and 'Organism: '

        """
        #---------------------
        # OUTPUT:
        output_project:dict = {}
        output_creators:dict  = {}
        output_organisms:dict  = {}

        output_simple :list = []


        #---------------------
        # GET containing_project_id:

        resource_ = self.json_for_resource(type_= 'projects', id_ = containing_project_id)
        output_project['title'] = resource_['data']['attributes']['title']
        output_project['description'] = resource_['data']['attributes']['description']

        output_simple.append('Project: '+ output_project['title'])


        #---------------------
        # GET model_creators:
        if len(model_creators) > 0 and isinstance(model_creators, list):

            for creator_ in model_creators:
                
                output_creators[creator_] = {}

                resource_ = self.json_for_resource(type_= 'people', id_ = creator_)

                output_creators[creator_]['first_name'] = resource_['data']['attributes']['first_name']
                output_creators[creator_]['last_name'] = resource_['data']['attributes']['last_name']
                output_creators[creator_]['orcid'] = resource_['data']['attributes']['orcid']
                output_creators[creator_]['name'] = output_creators[creator_]['first_name'] + ' ' + output_creators[creator_]['last_name']
                output_creators[creator_]['description'] = output_creators[creator_]['name'] + ' ' + output_creators[creator_]['orcid']

                output_simple.append('Creator: '+ output_creators[creator_]['description'])

        else:
            if not isinstance(model_creators, list):
                raise ValueError('check_model_vars: model_creators should be a list')

        #---------------------
        # GET model_organisms:
        if len(model_organisms) > 0 and isinstance(model_organisms, list):

            for organism_ in model_organisms:
            
                output_organisms[organism_] = {}

                resource_ = self.json_for_resource(type_= 'organisms', id_ = organism_)

                output_organisms[organism_]['title'] = resource_['data']['attributes']['title']
                output_organisms[organism_]['concept_uri'] = resource_['data']['attributes']['concept_uri']
                output_organisms[organism_]['ontology_id'] = resource_['data']['attributes']['ontology_id']

                output_organisms[organism_]['description'] = output_organisms[organism_]['title'] + ' ' + output_organisms[organism_]['concept_uri']

                output_simple.append('Organism: '+ output_organisms[organism_]['description'])

        else:
            if not isinstance(model_organisms, list):
                raise ValueError('check_model_vars: model_organisms should be a list')

        return output_project, output_creators, output_organisms, output_simple
    


    def add_model(self, 
                  model_metadata_yml: str,
                  model_filename: str,
                  model_filepath: str,
                  containing_project_id : int,
                  model_title: str,

                  model_creators: list[int] = [],
                  model_organisms: list[int] = [],

                  model_content_type: str =  'text/x-python3', 
                  access_: str = 'no_access', license_: str = 'notspecified',
                  model_type: str = 'AI/ML', model_format: str = 'Python code',
                  model_environment: str = 'Python'
                ) -> None: 
        """ add_model: Add a model to a FAIRDOM-SEEK instance

            INPUT:
                model_metadata_yml      = model metadata yaml file (str)
                model_filename          = the model filename (i.e., without path) (str)
                model_filepath          = the model filepath
                containing_project_id   = FAIRDOM-SEEK project to associate model with (int) 
                model_title             = model title for FAIRDOM-SEEK 
                model_creators          = the creators of the model has to be FAIRDOM-SEEK id's i.e., int (list of int)
                model_organisms         = the organisms associated with the model has to be FAIRDOM-SEEK id's i.e., int (list of int)
                model_content_type      = the model content (mime) type (strm default: text/xml)
                access_                 = the access policy (str, default: no_access)
                license_                = the license (in FAIRDOM-SEEK) (str, default: notspecified)
                model_type              = the model type (in FAIRDOM-SEEK) (str, default: AI/ML)
                model_format            = the model format (in FAIRDOM-SEEK) (str, default: Python code)
                model_environment       = the model environment (in FAIRDOM-SEEK) (str, default: Python)
                
                Note: access_, license_, model_type, model_format, model_environment will throw a Value error if the
                     variable defined does not match those expected for FAIRDOM-SEEK (vers 1.17)

            OUTPUT:
                None, submits model to FAIRDOM-SEEK instance

        """


        #--------------------------------
        # LOAD yaml metadata
        self.load_ml_metadata(filepath=model_metadata_yml)
        description_ = self.make_description()

        #---------------------------------
        # Check
        if access_ not in list(self.access_policy_.keys()):
            raise ValueError(f'ERROR! access_ must be one of: {list(self.access_policy_.keys())} ')
        
        if license_ not in list(self.license_.keys()):
            raise ValueError(f'ERROR! license_ must be one of: {list(self.license_.keys())} ')        

        if model_type not in self.SEEK_model_types_list:
            raise ValueError(f'ERROR! model_type must be one of: {self.SEEK_model_types_list} ')   

        if model_format not in self.SEEK_model_formats_list:
            raise ValueError(f'ERROR! model_format must be one of: {self.SEEK_model_formats_list} ')   
        
        if model_environment not in self.SEEK_model_recommended_envs_list:
            raise ValueError(f'ERROR! model_environment must be one of: {self.SEEK_model_recommended_envs_list} ')   

        #---------------------------------
        # Define the placeholder information for the content blob. 
        # For now just the filename and mime type are provided.

        local_blob = {
                        'original_filename' : model_filename, 
                        'content_type' : model_content_type  
                    }

        #---------------------------------
        # Next set up the attributes for the model and include the content blob details. 
        # This also shows the intent that content blobs will be provided. Although in this 
        # case there is only one content blob, for Models there could potentially be more which can be described.

        model = {}
        model['data'] = {}

        model['data']['type'] = 'models'

        model['data']['attributes'] = {}
        model['data']['attributes']['title'] = model_title
        model['data']['attributes']['policy'] = {'access':access_}
        model['data']['attributes']['license'] = license_
        model['data']['attributes']['description'] = description_
        model['data']['attributes']['model_type'] = model_type
        model['data']['attributes']['model_format'] = model_format
        model['data']['attributes']['environment'] = model_environment
        #model['data']['attributes']['model_image_link'] = None

        model['data']['relationships'] = {}
        model['data']['relationships']['projects'] = {}
        model['data']['relationships']['projects']['data'] = [{'id' : str(containing_project_id), 'type' : 'projects'}]

        #------------------
        # add model creators
        if len(model_creators) > 0 and isinstance(model_creators, list):
            
            model['data']['relationships']['creators'] = {}
            model['data']['relationships']['creators']['data'] = []

            for person_ in model_creators:
                
                model['data']['relationships']['creators']['data'].append({"id" : person_, "type": "people"})

        else:
            raise ValueError('add_model: model_creators must be a list even if its a single item')

        #------------------
        # add model organisms
        if len(model_organisms) > 0 and isinstance(model_organisms, list):
            
            model['data']['relationships']['creators'] = {}
            model['data']['relationships']['creators']['data'] = []

            for organism_ in model_organisms: 
                
                model['data']['relationships']['creators']['data'].append({"id" : organism_, "type": "organisms"})
        
        else:
            raise ValueError('add_model: model_organisms must be a list even if its a single item')

        #------------------
        model['data']['attributes']['content_blobs'] = [local_blob]

        #---------------------------------
        # Register the Model. The resulting JSON contains the content blob element, 
        # but this is currently blank.

        r = self.session.post(self.base_url + '/models', json=model)
        r.raise_for_status()

        
        populated_model = r.json()
        
        #print(populated_model)
        self.pretty_print_(populated_model)

        blob_url = populated_model['data']['attributes']['content_blobs'][0]['link']

        with open(model_filepath, 'rb') as file_:
            upload = self.session.put(blob_url, data=file_, headers={'Content-Type': 'text/xml'})
        upload.raise_for_status()





    def load_yaml(self, filepath: str, dump_indentation: int = 4):
        """ load_yaml: Load a yaml file

            INPUT:
                filepath           = filepath of the model metadata file
                dump_indentation   = number of idents for the config dump; default: 4
            
            OUTPUT: 
                content
                content_dump
        
        """        

        #-----------------
        # Use pyyaml to open and load configuration file
        with open(filepath) as f:

            try:
                content = yaml.safe_load(f)
                content_dump = yaml.dump(content, indent=dump_indentation)

            except yaml.YAMLError as e:

                print('Error loading config: %s', e)

        #-----------------------
        #
        return content, content_dump



    def load_ml_metadata(self, filepath: str)-> None:
        """ load_ml_metadata: Load a ML yaml file

            INPUT:
                filepath           = filepath of the model metadata file
            
            OUTPUT: 
                None, set load_yaml - content as self.metadata
                      set load_yaml - content_dump as self.metadata_dump
        """
        self.filepath = os.path.normpath(filepath)
        content, content_dump = self.load_yaml(self.filepath)
        
        self.metadata = content
        self.metadata_dump = content_dump



    def load_seek_terms(self, path_:str = '.\SEEK_yaml') -> None:
        """ load_seek_terms: Load SEEK yaml terms

            INPUT:
                path_ = path to SEEK files (str, default: '.\SEEK_yaml')

            OUTPUT:
                None, 


        """
        self.SEEK_model_types, _ = self.load_yaml(os.path.join(path_,'model_types.yml'))
        self.SEEK_model_formats, _ = self.load_yaml(os.path.join(path_,'model_formats.yml'))
        self.SEEK_model_recommended_envs, _ = self.load_yaml(os.path.join(path_,'model_recommended_environments.yml'))

        for key_ in self.SEEK_model_types:
            self.SEEK_model_types_list.append(self.SEEK_model_types[key_]['title'])

        for key_ in self.SEEK_model_formats:
            self.SEEK_model_formats_list.append(self.SEEK_model_formats[key_]['title'])

        for key_ in self.SEEK_model_recommended_envs:
            self.SEEK_model_recommended_envs_list.append(self.SEEK_model_recommended_envs[key_]['title'])



    def json_for_resource(self, 
                          type_:str, id_: int, 
                          header_ = {"Content-type": "application/vnd.api+json",
                                        "Accept": "application/vnd.api+json",
                                        "Accept-Charset": "ISO-8859-1"}
                                        ) :    
        """ json_for_resource: JSON for resource
        
            INPUT: 
                type_   = SEEK type
                id_     = SEEK ID
                header_ = Request header
            
            OUTPUT:
                r.json() = 
                
        """
        if self.token_ is not None:
            header_["Authorization"] = 'Token ' + self.token_
            print(header_)
            

        r = self.session.get(self.base_url + "/" + type_ + "/" + str(id_), headers= header_)
        
        #-----------------
        # If response is not 200 
        if (r.status_code != 200):
            print(r.json())
        
        r.raise_for_status()

        return r.json()



    def list_metadata(self, 
                      type_: str, 
                      header_: dict = {"Content-type": "application/vnd.api+json",
                                "Accept": "application/vnd.api+json",
                                "Accept-Charset": "ISO-8859-1"}):
        """ list_extended_metadata: List extended metadata

                INPUT:
                    type_   = SEEK type (str, default: 'extended_metadata_type')
                    header_ = request header (dict, default: {"Content-type": "application/vnd.api+json",
                                                            "Accept": "application/vnd.api+json",
                                                            "Accept-Charset": "ISO-8859-1"})

                OUTPUT:
                    r.json() = request json        

        """
        if self.token_ is not None:
            header_["Authorization"] = 'Token ' + self.token_
            print(header_)
    
        r = requests.get(self.base_url + "/" + type_ , headers=header_)
        r.raise_for_status()
        return r.json()        



    def list_extended_metadata(self, 
                               type_: str = 'extended_metadata_type', 
                               header_: dict = {"Content-type": "application/vnd.api+json",
                                        "Accept": "application/vnd.api+json",
                                        "Accept-Charset": "ISO-8859-1"}):
        """ list_extended_metadata: List extended metadata

                INPUT:
                    type_   = SEEK type (str, default: 'extended_metadata_type')
                    header_ = request header (dict, default: {"Content-type": "application/vnd.api+json",
                                                            "Accept": "application/vnd.api+json",
                                                            "Accept-Charset": "ISO-8859-1"})

                OUTPUT:
                    r.json() = request json        

        """
        if self.token_ is not None:
            header_["Authorization"] = 'Token ' + self.token_
            print(header_)

        r = requests.get(self.base_url + "/" + type_ , headers=header_)
        r.raise_for_status()
        return r.json()
    


    def get_extended_metadata(self, id_: int, type_:str  = 'extended_metadata_type', 
                              header_: dict = {"Content-type": "application/vnd.api+json",
                                        "Accept": "application/vnd.api+json",
                                        "Accept-Charset": "ISO-8859-1"}) :
        """ get_extended_metadata: Get extended metadata

                INPUT:
                    id_     = SEEK ID (int)
                    type_   = SEEK type (str, default: 'extended_metadata_type')
                    header_ = request header (dict, default: {"Content-type": "application/vnd.api+json",
                                                            "Accept": "application/vnd.api+json",
                                                            "Accept-Charset": "ISO-8859-1"})

                OUTPUT:
                    r.json() = request json

        """
        if self.token_ is not None:
            header_["Authorization"] = 'Token ' + self.token_
            print(header_)

        r = requests.get(self.base_url + "/" + type_ + "/" + str(id_), headers=self.headers)
        r.raise_for_status()
        return r.json()



    def make_description(self, print_:bool = False) -> str:
        """ make_description: Make the model description

            INPUT:
                print_ = whether to print the description to the terminal (bool, default: False)

            OUTPUT:
                the_description = the model's description (str)


        """
        model_ID    = self.metadata['ml_model_configuration']['model_identification']['ID']
        model_type_name  = self.metadata['ml_model_configuration']['model_identification']['name'] 
        model_vers  = self.metadata['ml_model_configuration']['model_identification']['version'] 


        #-------------------------------
        # Model publication
        #-------------------------------
        model_publication_authors = self.metadata['ml_model_configuration']['model_identification']['author']
        model_publication_doi =  self.metadata['ml_model_configuration']['model_identification']['doi']
        model_publication = {
                                'authors' : model_publication_authors.replace('&', '').split('.,'), 
                                'doi'     :model_publication_doi

                            }
        

        #-------------------------------
        # Model description
        #-------------------------------
        model_file          = self.metadata['ml_model_configuration']['model_description']['config_files']['model_file']
        model_learner       = self.metadata['ml_model_configuration']['model_description']['learner']
        model_type          = self.metadata['ml_model_configuration']['model_description']['model_type']
        
        model_language      = self.metadata['ml_model_configuration']['model_description']['language'][0]['name']
        model_language_vers = self.metadata['ml_model_configuration']['model_description']['language'][1]['version']
        
        model_time_int      = self.metadata['ml_model_configuration']['model_description']['input_time_interval']['description']
        model_aggregation   = self.metadata['ml_model_configuration']['model_description']['input_time_interval']['aggregation']['description']
        if model_aggregation == 'NaN':
            model_aggregation = 'No aggregation method is applied (set to "NaN").'


        model_package_requirements = '' 
        for package in self.metadata['ml_model_configuration']['model_description']['packages']:
            model_package_requirements = model_package_requirements + '* Package: ' + package['package'] +'\n'
            model_package_requirements = model_package_requirements + '* Class: ' + package['class'] +'\n'
            model_package_requirements = model_package_requirements + '* Version: ' + package['version'] +'\n'

        
        #-------------------------------
        # Model summary
        #-------------------------------
        model_description_  = self.metadata['ml_model_configuration']['model_description']['description']

        
        #-------------------------------
        # Model training info
        #-------------------------------
        model_training_instance  = str(self.metadata['ml_model_configuration']['training_information']['number_of_instances']  )
        #model_training_hyper     = self.metadata['ml_model_configuration']['training_information']['hyperparameters']   
        model_training_hyper = ''
        for hyper_param in self.metadata['ml_model_configuration']['training_information']['hyperparameters']:
            model_training_hyper = model_training_hyper + ' * ' + hyper_param + ': ' + str(self.metadata['ml_model_configuration']['training_information']['hyperparameters'][hyper_param]) + '\n'

        model_training_valid = self.metadata['ml_model_configuration']['training_information']['validation']


        #------------------------------
        # INPUT Table
        #-------------------------------
        input_table_header = '**Features**\n | **Name**                           | **Type**          | **Description**                           | **Units** | **Lag** | **Scaling** | **Expected Min** | **Expected Max** |\n| ---------------------------------- | ----------------- | ----------------------------------------- | --------- | ------- | ----------- | ---------------- | ---------------- |\n'
        input_txt = ''
        for input_ in self.metadata['ml_model_configuration']['inputs']['features']:
            input_txt = input_txt  + ' | ' + input_['name'] + ' | ' + input_['type'] + ' | ' + input_['description'] + ' | ' + input_['units'] + ' | ' + str(input_['lag']) + ' | ' + input_['feature_scaling'] + ' | ' + str(input_['expected_range']['min']) + ' | ' + str(input_['expected_range']['max']) + '\n'
        input_txt = input_table_header + input_txt 


        #-----------------------------
        # OUTPUT Table
        #-------------------------------
        output_table_header = '**Model Output**\nThe model predicts:\n| **Name**                     | **Description**                            | **Units** | **Forecast Horizon** | **Scaling** | **Expected Min** | **Expected Max** |\n| ---------------------------- | ------------------------------------------ | --------- | -------------------- | ----------- | ---------------- | ---------------- |\n'
        output_txt = ''
        for output_ in self.metadata['ml_model_configuration']['outputs']['information']:
            output_txt = output_txt  + ' | ' + output_['name'] + ' | ' + output_['description']  + ' | ' + output_['units'] + ' | ' + str(output_['forecast_horizon']) + ' | ' + output_['feature_scaling'] + ' | ' + str(output_['expected_range']['min']) + ' | ' + str(output_['expected_range']['max']) + '\n'
        output_txt = output_table_header + output_txt 


        #------------------------------
        # JOIN all the texts
        #-------------------------------
        model_identification_text = f'**Model Identification:** \nThe model is a {model_type_name} (version {model_vers} with the ID {model_ID}. Its authors are {model_publication_authors} and it is associated with the publication available at the DOI link: {model_publication_doi})'
        model_description_text = f'**Model Description:** \nThe model uses a {model_learner} and is classified as {model_type}. {model_description_}. It is implemented in {model_language} {model_language_vers}, and the corresponding model file is {model_file}. The implementation relies on:\n{model_package_requirements}'
        model_summary_text = f'**Model summary:** \n{model_description_}'
        model_time_interval_text = f'**Input Time Interval:** \n * {model_time_int}\n * {model_aggregation}'
        model_training_info_text = f'**Training Information:**  \nThe training dataset contains {model_training_instance} instances. The hyper parameters are:\n{model_training_hyper} \nThe model was validated using {model_training_valid}'

        
        #------------------------------
        # All the texts
        #-------------------------------
        the_description = model_identification_text + '\n\n' + model_description_text + '\n\n' + model_summary_text + '\n\n' + model_time_interval_text + '\n\n' + model_training_info_text + '\n\n' + input_txt + '\n\n' + output_txt


        
        #------------------------------
        # OUTPUT
        #-------------------------------        
        if print_:
            print(model_publication)
            print('\n\n')
            print(the_description)

        return the_description


