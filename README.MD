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

---

## ⚙️ FastAPI Endpoints

FastAPI → http://localhost:8000/docs

Streamlit → http://localhost:8501


| Method | Endpoint                            | Description          |
| ------ | ----------------------------------- | -------------------- |
| GET    | `/{project_id}/project_info/`       | Get Project Info     |
| GET    | `/{project_id}/db_config/`          | Get Db Config        |
| GET    | `/{project_id}/references/`         | Get References       |
| GET    | `/{project_id}/variables/`          | Get Variables        |
| GET    | `/{project_id}/list_models/`        | List Models Endpoint |
| GET    | `/{project_id}/metadata/{model_id}` | Get Model Metadata   |
| POST   | `/{project_id}/predict/{model_id}`  | Predict              |



---

## ⚙️ Configuration
The repository includes YAML configuration files in the `configs/` directory that define the available models, input/output features, and scaling information.

---

## 📝 License
This project is licensed under the MIT License.

---

## 📬 Contact
For questions, contact **David Camilo Corrales** at [David-Camilo.Corrales-Munoz@inrae.fr](mailto:David-Camilo.Corrales-Munoz@inrae.fr).

