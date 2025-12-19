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
library(rJava)
library(ranger)
library(yaml)
library(jsonlite)

# -----------------------------------------------------------------------------
# BASE_DIR: root of repository (two levels up when running from core/services/r)
# -----------------------------------------------------------------------------
# BASE_DIR <- normalizePath(file.path(dirname(getwd()), "..", ".."))
BASE_DIR <- "/app"

# -----------------------------------------------------------------------------
# Find metadata: try project-specific, then BASE_DIR/configs, then scan all projects
# Returns list(metadata=..., project_id=..., metadata_file=...)
# -----------------------------------------------------------------------------
find_metadata <- function(project_id, model_id) {
  # 1) try project-specific path if provided
  if (!is.null(project_id) && nzchar(project_id)) {
    mpath <- file.path(BASE_DIR, "projects", project_id, "configs", paste0(model_id, ".yaml"))
    if (file.exists(mpath)) {
      return(list(metadata = yaml::read_yaml(mpath), project_id = project_id, metadata_file = mpath))
    }
  }
  
  # 2) try top-level configs/ (if you keep a central folder)
  global_mpath <- file.path(BASE_DIR, "configs", paste0(model_id, ".yaml"))
  if (file.exists(global_mpath)) {
    return(list(metadata = yaml::read_yaml(global_mpath), project_id = NULL, metadata_file = global_mpath))
  }
  
  # 3) scan all projects' configs and try to match by filename OR model_identification$ID
  projects_dir <- file.path(BASE_DIR, "projects")
  if (dir.exists(projects_dir)) {
    proj_folders <- list.dirs(projects_dir, recursive = FALSE, full.names = TRUE)
    for (proj in proj_folders) {
      cfg_dir <- file.path(proj, "configs")
      if (!dir.exists(cfg_dir)) next
      yaml_files <- list.files(cfg_dir, pattern = "\\.ya?ml$", full.names = TRUE)
      for (yf in yaml_files) {
        # quick filename match
        if (tools::file_path_sans_ext(basename(yf)) == model_id) {
          return(list(metadata = yaml::read_yaml(yf), project_id = basename(proj), metadata_file = yf))
        }
        # otherwise inspect content (safe read)
        safe_read <- tryCatch(yaml::read_yaml(yf), error = function(e) NULL)
        if (!is.null(safe_read)) {
          mid <- safe_read$ml_model_configuration$model_identification$ID
          mname <- safe_read$ml_model_configuration$model_identification$name
          if (!is.null(mid) && mid == model_id) {
            return(list(metadata = safe_read, project_id = basename(proj), metadata_file = yf))
          }
          if (!is.null(mname) && mname == model_id) {
            return(list(metadata = safe_read, project_id = basename(proj), metadata_file = yf))
          }
        }
      }
    }
  }
  
  stop("Metadata file not found (checked project-specific, BASE_DIR/configs, and all projects' configs).")
}

# -----------------------------------------------------------------------------
# Load model (supports .rds and .RData; special handling for M5)
# -----------------------------------------------------------------------------
load_r_model <- function(project_id, metadata) {
  model_file_rel <- metadata$ml_model_configuration$model_description$config_files$model_file
  model_path <- file.path(BASE_DIR, "projects", project_id, "models", model_file_rel)
  if (!file.exists(model_path)) stop("Model file not found: ", model_path)
  
  learner <- metadata$ml_model_configuration$model_description$learner
  # If learner indicates M5 (or filename ends with .RData), apply special M5 handling
  if (!is.null(learner) && tolower(learner) == "m5") {
    M5env <- new.env()
    load(model_path, envir = M5env)
    serialized_file <- metadata$ml_model_configuration$model_description$config_files$serialized_model_file
    if (is.null(serialized_file) || !nzchar(serialized_file)) {
      stop("M5 model requires 'serialized_model_file' in metadata config_files.")
    }
    serialized_path <- file.path(BASE_DIR, "projects", project_id, "models", serialized_file)
    if (!file.exists(serialized_path)) stop("M5 serialized file not found: ", serialized_path)
    M5env$M5model$classifier <- .jcall("weka.core.SerializationHelper", "Ljava/lang/Object;", "read", serialized_path)
    model_obj <- M5env$M5model
    return(model_obj)
  }
  
  # .rds
  if (grepl("\\.rds$", model_path, ignore.case = TRUE)) {
    return(readRDS(model_path))
  }
  
  # .RData (load into env and try to pick the right object)
  if (grepl("\\.rdata$", model_path, ignore.case = TRUE)) {
    temp_env <- new.env()
    load(model_path, envir = temp_env)
    objs <- ls(envir = temp_env)
    if (length(objs) == 0) stop("No objects found in RData file: ", model_path)
    # Try finding an object with expected model classes (ranger, cubist, M5P, rpart, randomForest)
    for (nm in objs) {
      obj <- get(nm, envir = temp_env)
      if (inherits(obj, c("ranger", "Cubist", "cubist", "M5P", "rpart", "randomForest"))) {
        return(obj)
      }
    }
    # Fallback: return first object
    return(get(objs[1], envir = temp_env))
  }
  
  stop("Unsupported model file extension for: ", model_path)
}

# -----------------------------------------------------------------------------
# Utility: Extract the primary outputs metadata (safe)
# -----------------------------------------------------------------------------
get_output_info <- function(metadata) {
  outputs <- metadata$ml_model_configuration$outputs
  # prefer "information" -> list first entry
  if (!is.null(outputs$information) && length(outputs$information) >= 1) {
    return(outputs$information[[1]])
  }
  # fallback to "predictions"
  if (!is.null(outputs$predictions) && length(outputs$predictions) >= 1) {
    return(outputs$predictions[[1]])
  }
  # minimal fallback
  return(list(name = "prediction", description = "", units = "", feature_scaling = "none"))
}

# -----------------------------------------------------------------------------
# API endpoint
#* @post /predict
#* @param project_id The project identifier
#* @param model_id The model identifier (e.g. "0002_[R]_penicillin_RF")
#* @param req The request containing input JSON data
#* @response 200 Returns predictions (unified format)
function(project_id, model_id, req) {
  # Parse raw body in any case (robust)
  body_raw <- tryCatch(jsonlite::fromJSON(req$postBody, simplifyVector = FALSE), error = function(e) NULL)
  
  # Allow project_id/model_id to be passed either as function args or inside body
  if ((is.null(project_id) || !nzchar(project_id)) && !is.null(body_raw$project_id)) {
    project_id <- body_raw$project_id
  }
  if ((is.null(model_id) || !nzchar(model_id)) && !is.null(body_raw$model_id)) {
    model_id <- body_raw$model_id
  }
  
  if (is.null(body_raw$input_data) && !is.null(body_raw$req) && !is.null(body_raw$req$input_data)) {
    # Accept Python-forwarded body shape { "req": { "input_data": {...} } }
    input_data <- body_raw$req$input_data
  } else {
    input_data <- body_raw$input_data
  }
  
  if (is.null(model_id) || !nzchar(model_id)) {
    return(list(error = "Missing 'model_id' in request (either URL param or JSON body)."))
  }
  
  # Try to find metadata and project
  meta_info <- tryCatch(find_metadata(project_id, model_id), error = function(e) return(list(error = e$message)))
  if (!is.null(meta_info$error)) return(list(error = meta_info$error))
  
  metadata <- meta_info$metadata
  resolved_project <- meta_info$project_id
  # If project was not provided and not found, fall back to param
  if (is.null(resolved_project) || !nzchar(resolved_project)) {
    # if metadata was found in BASE_DIR/configs (global), the user must provide project_id or metadata may include project reference
    if (!is.null(project_id) && nzchar(project_id)) {
      resolved_project <- project_id
    } else {
      # try to read 'project' entry inside metadata (if present)
      pr_ref <- metadata$ml_model_configuration$model_identification$project
      if (!is.null(pr_ref)) {
        # If project: "../project_info.yaml" we try to find parent folder; otherwise leave NULL
        # Keep resolved_project as NULL but continue (model file paths were discovered earlier in find_metadata)
        resolved_project <- pr_ref
      } else {
        # no project info: attempt to continue but warn
        resolved_project <- NULL
      }
    }
  }
  
  # Verify language indicates R
  languages <- metadata$ml_model_configuration$model_description$language
  lang_names <- character(0)
  if (!is.null(languages)) {
    # each language entry can be a list with 'name' element
    lang_names <- tolower(unlist(lapply(languages, function(x) if (is.list(x) && !is.null(x$name)) x$name else as.character(x))))
  }
  if (!("r" %in% lang_names)) {
    return(list(error = paste0("Model '", model_id, "' metadata does not indicate language R. Found: ", paste(lang_names, collapse = ", "))))
  }
  
  # Input_data check
  if (is.null(input_data)) {
    return(list(error = "Missing 'input_data' in request body."))
  }
  
  # Build new_data data.frame (support named list or a data.frame like structure)
  new_data <- tryCatch({
    # if the input_data is already a list of named vectors, convert to data.frame with one row
    as.data.frame(input_data, stringsAsFactors = FALSE)
  }, error = function(e) {
    return(list(error = paste0("Failed to convert input_data to data.frame: ", e$message)))
  })
  if (is.list(new_data) && !is.data.frame(new_data) && !is.null(new_data$error)) return(new_data)
  
  # Load model object
  model_obj <- tryCatch(load_r_model(resolved_project, metadata), error = function(e) return(list(error = e$message)))
  if (is.list(model_obj) && !is.null(model_obj$error)) return(model_obj)
  
  # Logging
  nrows <- if (is.data.frame(new_data)) nrow(new_data) else NA
  cat(sprintf("[R API] Predict requested - project: %s | model: %s | rows: %s\n", 
              ifelse(is.null(resolved_project), "<unknown>", resolved_project), model_id, nrows))
  
  # Prediction logic depending on class
  result <- tryCatch({
    if (inherits(model_obj, "cubist") || inherits(model_obj, "Cubist")) {
      predict(model_obj, new_data)
    } else if (inherits(model_obj, "ranger")) {
      predict(model_obj, new_data)$predictions
    } else if (inherits(model_obj, "rpart")) {
      predict(model_obj, new_data, type = "vector")
    } else if (inherits(model_obj, "M5P")) {
      predict(model_obj, new_data)
    } else {
      # fallback: try generic predict
      predict(model_obj, new_data)
    }
  }, error = function(e) {
    list(error = paste0("Prediction error: ", e$message))
  })
  
  if (is.list(result) && "error" %in% names(result)) return(result)
  
  # Compose response in the SAME format as Python FastAPI
  out_info <- get_output_info(metadata)
  response <- list(
    output_model = list(
      list(
        metadata = list(
          name = out_info$name,
          description = out_info$description,
          units = out_info$units,
          feature_scaling = out_info$feature_scaling,
          model_info = metadata$ml_model_configuration$model_identification
        ),
        prediction = result
      )
    )
  )
  
  return(response)
}
