# README: Machine Learning Model API

## Overview
This repository provides a REST API for serving Machine Learning models using R and the Plumber framework. The API allows users to list available models, retrieve metadata, and make predictions based on input data.

### Author Information
- **Author**: David Camilo Corrales
- **Email**: David-Camilo.Corrales-Munoz@inrae.fr
- **Date**: 2025-03-18
- **Description**: This script serves ML models via a REST API using Plumber.

## Prerequisites
Ensure that you have R and the necessary dependencies installed before running the API.

### Required R Libraries:
- plumber
- RWeka
- Cubist
- yaml
- rJava
- ranger

## Installation
Before running your API script, execute the `install_dependencies.R` script to ensure all required packages are installed:

```r
source("install_dependencies.R")
```

## Running the API Server
After saving the script, start the Plumber API server with the following command:

```r
library(plumber)
r <- plumb("app.R")  # Specify the path to your script
r$run(host = "0.0.0.0", port = 8081)
```

## Available API Endpoints

### 1. List Available Models
Retrieve a list of available ML models based on metadata files.

#### Endpoint:
```
GET /list_models
```
#### Response:
```json
[
  "Random Forest",
  "Cubist",
  "CART",
  "M5"
]
```

### 2. Retrieve Model Metadata
Retrieve metadata for a specific model.

#### Endpoint:
```
GET /metadata?model_name=<MODEL_NAME>
```
#### Example Request:
```
GET http://localhost:8081/metadata?model_name=random_forest
```
#### Example Response:
```json
{
  "ml_model_configuration": {
    "model_identification": {
      "name": "Random Forest",
      "description": "A random forest regression model."
    },
    "outputs": {
      "predictions": [
        {
          "name": "Yield",
          "description": "Predicted yield of the system.",
          "units": "kg/m^3"
        }
      ]
    }
  }
}
```

### 3. Make Predictions
Use a trained ML model to generate predictions based on input features.

#### Endpoint:
```
POST /predict
```
#### Example Request (JSON Body):
```json
{
  "model": "CUBIST",
  "req": {
    "input_data": {
      "temperature": 298.22,
      "pH": 6.4472,
      "dissolved_oxygen_concentration": 30,
      "agitator": 100,
      "CO2_percent_in_off_gas": 0.089514,
      "oxygen_in_percent_in_off_gas": 0.19595,
      "vessel_volume": 58479,
      "sugar_feed_rate": 8
    }
  }
}
```
#### Example Curl Request:
```sh
curl -X POST "http://localhost:8081/predict" -H "Content-Type: application/json" -d '{
  "model": "CUBIST",
  "req": {
    "input_data": {
      "temperature": 298.22,
      "pH": 6.4472,
      "dissolved_oxygen_concentration": 30,
      "agitator": 100,
      "CO2_percent_in_off_gas": 0.089514,
      "oxygen_in_percent_in_off_gas": 0.19595,
      "vessel_volume": 58479,
      "sugar_feed_rate": 8
    }
  }
}'
```
#### Example Response:
```json
{
  "predictions": [
    {
      "name": "Yield",
      "description": "Predicted yield of the system.",
      "units": "kg/m^3",
      "value": 45.67
    }
  ],
  "model_info": {
    "name": "CUBIST",
    "description": "A Cubist regression model."
  }
}
```

## Running the API via Browser
To test API endpoints via a web browser, you can visit:

```
http://localhost:8081/metadata?model_name=random_forest
```

## Running the API via PowerShell
To make predictions using PowerShell:

```powershell
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8081/predict" -Headers @{"Content-Type"="application/json"} -Body '{
  "model": "CUBIST",
  "req": {
    "input_data": {
      "temperature": 298.22,
      "pH": 6.4472,
      "dissolved_oxygen_concentration": 30,
      "agitator": 100,
      "CO2_percent_in_off_gas": 0.089514,
      "oxygen_in_percent_in_off_gas": 0.19595,
      "vessel_volume": 58479,
      "sugar_feed_rate": 8
    }
  }
}'

# Convert and print JSON output
$response | ConvertTo-Json -Depth 10
```

## Notes
- Ensure that all model metadata files are stored in the `config/` directory.
- Trained models should be placed in the `models/` directory.
- The API currently supports Random Forest (ranger), Cubist, CART (rpart), and M5 models.

## Troubleshooting
- If the API fails to start, ensure that all dependencies are correctly installed by running:
  ```r
  install.packages(c("plumber", "RWeka", "Cubist", "yaml", "rJava", "ranger"))
  ```
- If a model is not found, verify that the corresponding YAML metadata file exists and contains the correct model name.

## Future Enhancements
- Implement authentication and authorization for secure API access.
- Extend model support to additional ML algorithms.
- Provide a web-based UI for interacting with the API.

---

This README provides clear installation steps, API usage instructions, example requests, and troubleshooting tips. Let me know if you need any additional details!

