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
---

## ⚙️ FastAPI Endpoints

You can explore the FastAPI endpoints at: http://localhost:8000/docs

This API allows you to query metadata, variables, models, and make predictions for different ML projects.

Example project:

- **Project Name:** IndPenSim
- **Project ID:** P0001

### Description:**
The dataset corresponds to industrial-scale penicillin fermentation simulations (Paul & Thomas, 1996; Goldrick et al., 2015, 2019). It contains 100 batches with 2238 variables each. 39 variables correspond to process variables, and 2199 variables correspond to Raman spectra. Data was collected every 12 minutes, and the first 90 batches represent normal operation under different control strategies. The last 10 batches contain induced faults for process deviation testing.

| Method | Endpoint                            | Description                                                                                                                      |
| ------ | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/{project_id}/project_info/`       | Get project metadata including description, DB config, references, and variables. Example: `GET /P0001/project_info/`            |
| GET    | `/{project_id}/db_config/`          | Get database configuration for the project. Example: `GET /P0001/db_config/`                                                     |
| GET    | `/{project_id}/references/`         | Get list of references for the project. Example: `GET /P0001/references/`                                                        |
| GET    | `/{project_id}/variables/`          | Get all variables with descriptions, units, and types. Example: `GET /P0001/variables/`                                          |
| GET    | `/{project_id}/list_models/`        | List all models available for the project. Example: `GET /P0001/list_models/`                                                    |
| GET    | `/{project_id}/metadata/{model_id}` | Get detailed metadata of a specific model, including input/output scalers and configuration. Example: `GET /P0001/metadata/0009_[Python]_penicillin_LSTM` |
| POST   | `/{project_id}/predict/{model_id}`  | Predict outputs using a specific model. Example: `POST /P0001/predict/0009_[Python]_penicillin_LSTM` with body:                                           |

---

##: 🖥️ Streamlit UI

Streamlit → http://localhost:8501


The Streamlit UI provides an interactive way to explore your ML projects, inspect models, and run predictions without directly interacting with the FastAPI endpoints.

**Streamlit → [http://localhost:8501](http://localhost:8501)**

### Features

**Project Selection:**  
Browse all available projects automatically detected in the `projects/` folder. Projects display human-readable names pulled from their `project_info.yaml`.

**Project Info:**  
View project description, database configuration, references, and variables directly in the sidebar.

**Model Selection:**  
Choose a model from the selected project and explore its metadata, including:

- **Overview:** description, programming language, packages, files  
- **Architecture:** input/output layers, LSTM or other layers  
- **Inputs & Outputs:** features and predictions  
- **Training Information:** number of instances, hyperparameters, validation strategy, experiment IDs  

**Run Predictions:**  
Enter input values interactively and send a prediction request to the FastAPI backend. Results are displayed immediately in the UI.

---

## ⚙️ Configuration
The repository includes YAML configuration files in the `configs/` directory that define the available models, input/output features, and scaling information.

---

## 📝 License
This project is licensed under the MIT License.

---

## 📬 Contact
For questions, contact **David Camilo Corrales** at [David-Camilo.Corrales-Munoz@inrae.fr](mailto:David-Camilo.Corrales-Munoz@inrae.fr).

