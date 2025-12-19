1- Run the installation script: 

Before running your API script, run the install_dependencies.R script to ensure all required packages are installed:

source("install_dependencies.R")

2- Run the Plumber API server:

After saving the script, run the Plumber API server with the following command:

# setwd("C:/Users/corrales/Documents/STAMM/ML_repository/Project_IndPenSim/services/r")



library(plumber)
r <- plumb("app.R")  # Specify the path to your script
r$run(host = "0.0.0.0", port = 8081)




Call services:

via browser: http://localhost:8081/metadata?model_name=random_forest


curl -Method Post -Uri "http://localhost:8081/predict" -Headers @{"Content-Type"="application/json"} -Body '{"model": "CUBIST", "req": {"input_data": [0.5, 1.2, 3.4, 2.1, 0.9, 1.5, 3.0, 2.7]}}'


curl -Method Post -Uri "http://localhost:8081/predict" -Headers @{"Content-Type"="application/json"} -Body '{
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



