<div style="text-align: center;">
  <img src="assets/ml_repo_logo.png" alt="ML Repository Logo" width="200"/>
</div>

This repository provides a FastAPI-based machine learning service for deploying soft sensors. The service allows users to send input data and receive predictions from different machine learning models.

## 🚀 Features
- Supports multiple ML models (e.g., Random Forest, LSTM, CUBIST, etc.).
- Uses pre-trained models.
- Scales input and output values automatically when required.
- Provides metadata for available models.
- Streamlit frontend to explore metadata and interact with the API.

---

## 📂 Repository Structure

The repository follows this structure:

```
model-registry/
├── UI-FastApi.py           # Streamlit UI to explore model metadata and call FastAPI
├── core/                   # FastAPI backend
│   ├── app.py              # Main FastAPI application
│   ├── model_registry.py   # Model registry logic
│
├── projects/               # Organized ML projects
│   ├── Project_E.Coli/     # Example project (empty structure shown)
│   ├── Project_IndPenSim/  # Example project with metadata and models
│       ├── project_info.yaml
│       ├── configs/        # Model metadata (YAML)
│       ├── models/         # Exported models & scalers
│       ├── services/       # Model services (e.g., R, Python, MATLAB)
│
├── assets/                 # Static assets (logos, etc.)
│   └── ml_repo_logo.png
└── README.md               # Documentation
```

---

## 📦 Installation

### 1️⃣ **Clone the Repository**
```sh
git clone https://gitlab.com/stamm-4m/model-registry.git
cd your-repo-folder
```
To run the app, navigate to the project folder (Project_IndPenSim) and follow these steps

### 🐳 Running with Docker

Build & Run
```sh
docker compose up --build -d

```
Stop
```sh
docker compose down

```

### 3️⃣ **URL**


FastAPI → http://localhost:8000/docs

Streamlit → http://localhost:8501

---

## 🚦 Running the API

Start the FastAPI service using Uvicorn (default port 443). To run the app, navigate to the project folder (Project_IndPenSim). Once dependencies are installed, you can start the FastAPI service by running the following command:

```sh
poetry run python -m app

```

After starting, the API will be available at:
```
http://localhost:443
```

To view interactive API documentation, open in a browser:
```
http://localhost:443/docs
```

---

## 📡 API Endpoints

### 🌱🔬 Get Project Information 

**Endpoint:** `GET /project_info/`

**Response Example:**
```json
{
  "db_config": {
    "db": "InfluxDB",
    "version": 2.7,
    "port": "8080",
    "bucket": "STAMM Bucket",
    "org_id": "9079c78425d0d055"
  },
  "description": "The dataset used in this work corresponds to a series of experiments that were subsequently utilized to produce a simulation of industrial- scale penicillin fermentation processes (Paul and Thomas, 1996) which describes all the component balances relating to the process variables (Goldrick et al., 2015, 2019). The dataset generated from the industrial-scale penicillin fermentation (IndPenSim) includes 100 batches with each dataset comprising 2238 variables of which 39 variables correspond to process variables (manual and automatic control and online and offline measurements) and the remaining 2199 spond to Raman spectra. Per batch sensors recorded data every 12 min with the average batch length being approximately 230 h. Out of the 100 batches, the first 90 batches were operated under “normal” conditions using three different control strategies: (I) controlled by a recipe driven approach; (II) controlled by an operator and (III) controlled by an Advanced Process Control (APC). The last 10 batches contains faults, resulting in process deviations (Goldrick et al., 2019).",
  "references": [
    {
      "id": "Paul1996",
      "authors": "Paul, G. and Thomas, S.",
      "title": "A structured model for hyphal differentiation and penicillin production using penicillium chrysogenum",
      "journal": "Biotechnology and bioengineering",
      "year": 1996,
      "doi": "10.1016/XXX",
      "apa": "Paul, G. C., & Thomas, C. R. (1996). A structured model for hyphal differentiation and penicillin production using Penicillium chrysogenum. Biotechnology and bioengineering, 51(5), 558-572."
    }
    ...
  ],
  "variables": [
    {
      "name": "Time (h)",
      "column_type": "Time",
      "units": "Hour",
      "renamed_variable": "time",
      "description": "Elapsed time in hours since the start of the experiment"
    },
    {
      "name": "Aeration rate(Fg:L/h)",
      "column_type": "Actuator",
      "units": "Fg:L/h",
      "renamed_variable": "aeration_rate",
      "description": "Rate of air supplied to the bioreactor per litre per hour"
    },
    {
      "name": "Agitator RPM(RPM:RPM)",
      "column_type": "Actuator",
      "units": "RPM",
      "renamed_variable": "agitator",
      "description": "Agitator speed in revolutions per minute, controlling mixing intensity"
    },
    {
      "name": "Sugar feed rate(Fs:L/h)",
      "column_type": "Actuator",
      "units": "L/h",
      "renamed_variable": "sugar_feed_rate",
      "description": "Rate at which sugar solution is fed into the bioreactor, measured in litres per hour"
    },
      ...
    {
      "name": "Viscosity(Viscosity_offline:centPoise)",
      "column_type": "Offline_measurement",
      "units": "centPoise",
      "renamed_variable": "viscosity",
      "description": "Offline measurement of broth viscosity, measured in centipoise"
    },
    {
      "name": "Batch ID",
      "column_type": "Experiment",
      "units": "-",
      "renamed_variable": "experiment_ID",
      "description": "Unique identifier for the batch or experiment run"
    }
  ]
}
```

### 🔍 List Available Models
**Endpoint:** `GET /list_models/`

**Response Example:**
```json
{
  "available_soft_sensors": [
    {
      "name": "random_forest",
      "model_identification": {
        "name": "random_forest",
        "version": "V.1.0",
        "UUID": "",
        "author": "Acosta-Pavas, J. C., Robles-Rodriguez, C. E., Griol, D., Daboussi, F., Aceves-Lara, C. A., & Corrales, D. C",
        "doi": "https://doi.org/10.1016/j.compchemeng.2024.108736",
        "creation_date": "22-01-2024",
        "project": "../project_info.yaml"
      }
    },
    {
      "name": "CART",
      "model_identification": {
        "name": "CART",
        "version": "V.1.0",
        "UUID": "",
        "author": "Acosta-Pavas, J. C., Robles-Rodriguez, C. E., Griol, D., Daboussi, F., Aceves-Lara, C. A., & Corrales, D. C",
        "doi": "https://doi.org/10.1016/j.compchemeng.2024.108736",
        "creation_date": "22-01-2024",
        "project": "../project_info.yaml"
      }
    },
    {
      "name": "SVM",
      "model_identification": {
        "name": "SVM",
        "version": "V.1.0",
        "UUID": "",
        "author": "Suarez, C., Astudillo A., Valencia-Mosquera J.F., Metcalfe B., Koehorst J.J., Castillo E. & Corrales, D. C",
        "doi": "",
        "creation_date": "26-02-2025",
        "project": "../project_info.yaml"
      }
    },
    {
      "name": "GBM",
      "model_identification": {
        "name": "GBM",
        "version": "V.1.0",
        "UUID": "",
        "author": "Suarez, C., Astudillo A., Valencia-Mosquera J.F., Metcalfe B., Koehorst J.J., Castillo E. & Corrales, D. C",
        "doi": "",
        "creation_date": "17-02-2025",
        "project": "../project_info.yaml"
      }
    },
    {
      "name": "LSTM",
      "model_identification": {
        "name": "LSTM",
        "version": "V.1.0",
        "UUID": "",
        "author": "Suarez, C., Astudillo A., Valencia-Mosquera J.F., Metcalfe B., Koehorst J.J., Castillo E. & Corrales, D. C",
        "doi": "",
        "creation_date": "17-02-2025",
        "project": "../project_info.yaml"
      }
    }
  ]
}
```

### 🛠 Get Model Metadata
**Endpoint:** `GET /metadata/{model_name}`

**Example Request:**
```
GET http://localhost:443/metadata/LSTM
```

**Response Example:**
```json
{
  "name": "LSTM",
  "model_identification": {
    "name": "LSTM",
    "version": "V.1.0",
    "UUID": "",
    "author": "Suarez, C., Astudillo A., Valencia-Mosquera J.F., Metcalfe B., Koehorst J.J., Castillo E. & Corrales, D. C",
    "doi": "",
    "creation_date": "17-02-2025",
    "project": "../projects/project_info.yaml"
  },
  "model_description": {
    "learner": "Long short-term memory (LSTM)",
    "model_type": "black box",
    "model_name": "LSTM without lag features [Python version]",
    "description": "This is not the soft sensor using the LSTM with lag features proposed in the paper (Metcalfe et al., 2025).",
    "language": [
      {
        "name": "python",
        "version": "3.12.7"
      }
    ],
    "config_files": {
      "model_file": "0009_[Python]_penicillin_LSTM.keras"
    },
    "packages": [
      {
        "package": "tensorflow",
        "version": "2.18.0",
        "classes": [
          "keras.layers.LSTM",
          "keras.layers.Dropout",
          "keras.layers.BatchNormalization",
          "keras.layers.Dense",
          "keras.models.Sequential",
          "keras.callbacks.EarlyStopping",
          "keras.optimizers.Adam"
        ]
      },
      {
        "package": "sklearn",
        "version": "1.5.2",
        "classes": [
          "preprocessing.MinMaxScaler"
        ]
      }
    ],
    "input_time_interval": {
      "time_interval": {
        "value": 12,
        "unit": "minutes"
      },
      "aggregation": {
        "method": "NaN",
        "description": "NaN"
      },
      "description": "One measurement every 12 minutes"
    }
  },
  "training_information": {
    "number_of_instances": 89800,
    "hyperparameters": {
      "batch_size": 512,
      "epochs": 100,
      "optimizer": {
        "name": "Adam",
        "learning_rate": 0.001,
        "description": "The Adam optimizer is used for training."
      },
      "loss_function": {
        "name": "Mean Squared Error (MSE)",
        "description": "MSE is used as the loss function to minimize the squared differences between predicted and actual values of penicillin concentration."
      },
      "callbacks": {
        "early_stopping": {
          "monitor": "val_loss",
          "patience": 10,
          "description": "Early stopping is used to halt training when the validation loss stops improving for 10 consecutive epochs."
        }
      }
    },
    "validation": "Train-test split with early stopping",
    "experiments_ID": [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 19, 20, 21, 22, 24, 25, 26, 27, 29, 30, 31, 33, 34, 36, 37, 38, 39, 40, 42, 43, 44, 45, 47, 48, 49, 50, 51, 53, 54, 55, 56, 57, 58, 59, 61, 62, 65, 66, 67, 69, 70, 71, 72, 73, 74, 75, 76, 77, 80, 81, 82, 83, 84, 85, 87, 88, 89, 90, 92, 93, 94, 95, 96, 97, 98, 99]
  },
  "input_features": [
    "sugar_feed_rate",
    "agitator",
    "temperature",
    "pH",
    "dissolved_oxygen_concentration",
    "vessel_volume",
    "CO2_percent_in_off_gas",
    "oxygen_in_percent_in_off_gas"
  ],
  "output_features": [
    "penicillin_concentration"
  ]
}
```

### 🔮 Make a Prediction
**Endpoint:** `POST /predict/`

**Example Request:**
```json
{
  "model": "CART",
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

**Example PowerShell Command:**
```powershell
$body = @"
{
  "model": "LSTM",
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
"@

$response = Invoke-RestMethod -Uri "http://localhost:443/predict/" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body

$response | ConvertTo-Json -Depth 10 | Out-File "response.json"

Get-Content response.json
```

**Response Example:**
```json
{
    "predictions":  [
                        {
                            "name":  "penicillin_concentration",
                            "value":  [
                                          [
                                              3.6946999993781889E-26
                                          ]
                                      ]
                        }
                    ]
}
```

---

## ⚙️ Configuration
The repository includes YAML configuration files in the `configs/` directory that define the available models, input/output features, and scaling information.

---

## 🛠 Development & Testing

### Running Unit Tests
```sh
pytest tests/
```

### Linting the Code
```sh
flake8 app.py model_registry.py
```

---

## 📝 License
This project is licensed under the MIT License.

---

## 📬 Contact
For questions, contact **David Camilo Corrales** at [David-Camilo.Corrales-Munoz@inrae.fr](mailto:David-Camilo.Corrales-Munoz@inrae.fr).

