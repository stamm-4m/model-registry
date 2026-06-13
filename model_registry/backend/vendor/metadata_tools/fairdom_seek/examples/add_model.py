""" add_model.py
        
    To add a new model to a FAIRDOM-SEEK instance (defined by base_url) a user can use the add_model function of model2seek
    
"""
from model2seek import model2seek


#------------------
# API Token
api_token = 'YOUR-TOKEN-FROM-FAIRDOM-SEEK'

#------------------
# Initialise Class
m2s = model2seek(
                base_url= 'https://sandbox7.fairdomhub.org', # the FAIRDOM-SEEK instance you want to add to / query
                token=api_token  # your API token
                )

#------------------
# Start a request session
m2s.start_session()

#------------------
# Add a model to the FAIRDOM-SEEK
m2s.add_model(
                model_metadata_yml = '0001_[python]_penicillin_RF.yaml', # Model metadata yaml file
                model_filename= 'test6_model',  # the name of the model's file
                model_filepath = 'test_model.py', # the filepath of the model
                containing_project_id = 17, # the project ID
                model_title = 'test_model_upload_api', # the title of the model's FAIRDOM-SEEK title
                model_creators= [2,3,4] # the model creator's FAIRDOM-SEEK person IDs
            )
