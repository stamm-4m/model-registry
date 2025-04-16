# =============================================================================
# R Script for Machine Learning Model API
# Author: David Camilo Corrales
# Email: David-Camilo.Corrales-Munoz@inrae.fr
# Date: 2025-03-18
# Description: This script serves ML models via a REST API using Plumber.
# =============================================================================

library(plumber)
library(RWeka)
library(Cubist)
library(yaml)
library(rJava)
library(ranger)

# =============================================================================
# Function: list_models
# Description: Lists available ML models based on metadata files.
# =============================================================================
list_models <- function() {
  metadata_dir <- "config/"
  all_files <- list.files(metadata_dir, pattern = "\\.yaml$", full.names = TRUE)
  model_list <- lapply(all_files, function(file) {
    yaml_content <- tryCatch(yaml::read_yaml(file), error = function(e) return(NULL))
    if (!is.null(yaml_content) && !is.null(yaml_content$ml_model_configuration$model_identification)) {
      return(yaml_content$ml_model_configuration$model_identification)
    }
    return(NULL)
  })
  return(Filter(Negate(is.null), model_list))
}

# =============================================================================
# API Endpoint: /list_models
# Description: Returns a list of available ML models.
# =============================================================================
#* @get /list_models
#* @response 200 Returns a list of available models
function() {
  return(list_models())
}


# =============================================================================
# Function: find_metadata_file
# Description: Finds the correct YAML metadata file based on the model name.
# =============================================================================
library(yaml)

find_metadata_file <- function(model_name) {
  metadata_dir <- "config/"
  all_files <- list.files(metadata_dir, pattern = "\\.yaml$", full.names = TRUE)
  for (file in all_files) {
    print(file)
    yaml_content <- tryCatch(yaml::read_yaml(file), error = function(e) return(NULL))
    print(yaml_content$ml_model_configuration$model_identification$name)
    if (!is.null(yaml_content) && 
        !is.null(yaml_content$ml_model_configuration$model_identification$name) &&
        yaml_content$ml_model_configuration$model_identification$name == model_name) {
      return(file)  # Return the file path if the model name matches
    }
  }
  
  stop("Metadata file not found for model: ", model_name)
}


# =============================================================================
# Function: load_metadata
# Description: Loads metadata from the corresponding YAML file.
# =============================================================================
load_metadata <- function(model_name) {
  metadata_path <- find_metadata_file(model_name)
  return(yaml::read_yaml(metadata_path))
}

# =============================================================================
# Function: load_model
# Description: Loads the ML model using its metadata.
# =============================================================================
load_model <- function(model_name) {
  metadata <- load_metadata(model_name)
  
  model_file <- file.path("models/", metadata$ml_model_configuration$model_description$config_files$model_file)
  
  if (!file.exists(model_file)) {
    stop("Model file not found: ", model_file)
  }
  
  if (metadata$ml_model_configuration$model_description$learner == "M5") {  # Check if the learner is M5
    print("Loading M5 model using RWeka")
    M5env <- new.env()
    load(model_file, envir = M5env)
    serialized_model_file <- file.path("models/", metadata$ml_model_configuration$model_description$config_files$serialized_model_file)
    M5env$M5model$classifier <- .jcall("weka.core.SerializationHelper", "Ljava/lang/Object;", "read", serialized_model_file)
    return(list(
      model = M5env$M5model,
      metadata = metadata
    ))
  } else {
    return(list(
      model = readRDS(model_file),
      metadata = metadata
    ))
  }
}


# =============================================================================
# API Endpoint: /metadata
# Description: Retrieves metadata for the requested model.
# =============================================================================
#* @get /metadata
#* @param model_name The model name (e.g., "RF", "CUBIST", "CART", "M5")
#* @response 200 Returns metadata for the model
function(model_name) {
  metadata <- tryCatch(load_metadata(model_name), error = function(e) return(list(error = e$message)))
  return(metadata)
}

# =============================================================================
# API Endpoint: /predict
# Description: Returns predictions using the requested model.
# =============================================================================
#* @post /predict
#* @param model The model name (e.g., "RF", "CUBIST", "CART", "M5")
#* @param req The request containing input JSON data
#* @response 200 Returns predictions
function(model, req) {
  print(paste("Requested model:", model))  # Debugging step
  
  # Load the model using tryCatch
  loaded_model <- tryCatch({
    load_model(model)
  }, error = function(e) {
    print(paste("Error loading model:", e$message))
    return(list(error = e$message))
  })
  
  # Check if model loading failed
  if (!is.null(loaded_model$error)) {
    return(list(error = paste("Failed to load model:", loaded_model$error)))
  }
  
  model_object <- loaded_model$model
  metadata <- loaded_model$metadata
  
  print(paste("Class of loaded model:", class(model_object)))  # Debugging step
  
  # Convert JSON input to data frame
  new_data <- as.data.frame(jsonlite::fromJSON(req$postBody, flatten = TRUE))
  colnames(new_data) <- gsub("req.input_data.", "", colnames(new_data))  # Remove the prefix
  print("Received data:")
  print(new_data)
  
  # Dynamically call the correct predict function based on model class
  predictions <- tryCatch({
    if (inherits(model_object, "cubist")) {
      print("Making predictions using Cubist model")
      result <- predict(model_object, new_data)  # Cubist models
    } else if (inherits(model_object, "ranger")) {
      print("Making predictions using Ranger model")
      result <- predict(model_object, new_data)$predictions  # Random Forest models
    } else if (inherits(model_object, "rpart")) {
      print("Making predictions using Rpart model")
      result <- predict(model_object, new_data, type = "vector")  # CART models
    } else if (inherits(model_object, "M5P")) {
      
      # Ensure RWeka is loaded
      if (!requireNamespace("RWeka", quietly = TRUE)) {
        print("Making predictions using M5P Weka model")
      }
      
      # Check if the model object is indeed an M5P object
      print(paste("Class of model after loading M5P:", class(model_object)))
      
      # Check the structure of the M5P object
      print("M5P model structure:")
      print(str(model_object))
      
      # Make the prediction using the generic RWeka predict() method for Weka models
      result <- tryCatch({
        prediction <- predict(model_object, new_data)  # Generic predict() for Weka models
        return(prediction)
      }, error = function(e) {
        print(paste("Error during prediction with M5P model:", e$message))
        return(list(error = e$message))
      })
      
    } else {
      stop("Unsupported model type:", class(model_object))
    }
    
    # Debugging: Print the result type and structure of predictions
    print("Predictions structure:")
    print(str(result)) 

    # Constructing the proper response with metadata and predictions
    
    print("Loaded metadata:")
    print(str(metadata))
    
    response <- list(
      predictions = list(
        list(
          name = metadata$ml_model_configuration$outputs$predictions[[1]]$name,  # Name from metadata
          description = metadata$ml_model_configuration$outputs$predictions[[1]]$description,  # Description from metadata
          units = metadata$ml_model_configuration$outputs$predictions[[1]]$units,  # Units from metadata
          feature_scaling = metadata$ml_model_configuration$outputs$predictions[[1]]$feature_scaling,  # Feature scaling
          value = result  # Prediction values
        )
      ),
      model_info = metadata$ml_model_configuration$model_identification  # Including model identification information
    )
    
    return(response)
    
  }, error = function(e) {
    print(paste("Prediction error:", e$message))
    return(list(error = e$message))
  })
  
  # If there was a prediction error, return it
  if (inherits(predictions, "list") && "error" %in% names(predictions)) {
    return(predictions)  # Return the prediction error if it failed
  }
  
  
}

