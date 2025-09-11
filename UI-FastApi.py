# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 19:37:21 2025

@author: David Camilo Corrales

"""
import streamlit as st
import requests
import json
import pandas as pd
import os
import yaml

# --- API Base ---
# API_BASE = "http://localhost:443"  # Adjust if running elsewhere

API_BASE = os.getenv("FASTAPI_URL", "http://localhost:8000")

# --- Sidebar: Project Selection ---
st.sidebar.title("🗂️ Project")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

if not os.path.exists(PROJECTS_DIR):
    st.sidebar.error(f"⚠️ Projects folder not found at {PROJECTS_DIR}")
    st.stop()

# Scan projects folder and read project_info.yaml
project_map = {}  # {project_ID: project_name}
for folder in os.listdir(PROJECTS_DIR):
    folder_path = os.path.join(PROJECTS_DIR, folder)
    info_file = os.path.join(folder_path, "project_info.yaml")
    if os.path.isdir(folder_path) and os.path.exists(info_file):
        with open(info_file, "r", encoding="utf-8") as f:
            info = yaml.safe_load(f)
            project_id = info.get("project_ID")
            project_name = info.get("project_name", folder)
            if project_id:
                project_map[project_id] = project_name

if not project_map:
    st.sidebar.error("⚠️ No projects found.")
    st.stop()

# Sidebar selectbox: show human-readable names, store project_ID
project_ids = list(project_map.keys())
project_names = [project_map[pid] for pid in project_ids]

selected_index = st.sidebar.selectbox(
    "Select a Project:",
    range(len(project_ids)),
    format_func=lambda i: project_names[i]
)
project_id = project_ids[selected_index]
project_name = project_names[selected_index]

# --- Fetch project info ---
PROJECT_INFO_URL = f"{API_BASE}/{project_id}/project_info/"
project_info = {}
try:
    resp = requests.get(PROJECT_INFO_URL)
    resp.raise_for_status()
    project_info = resp.json()
except requests.exceptions.RequestException as e:
    st.sidebar.error(f"⚠️ Could not fetch project info: {e}")

# --- Sidebar: Project Info Expander ---
with st.sidebar.expander("ℹ️ Project Info"):
    if project_info:
        st.markdown(f"### {project_name}")
        st.write(project_info.get("description", "No description available."))
        st.subheader("DB Config")
        st.json(project_info.get("db_config", {}))
        st.subheader("References")
        st.json(project_info.get("references", []))
        st.subheader("Variables")
        st.json(project_info.get("variables", []))
    else:
        st.info("Project info not available.")

# --- Fetch available models ---
LIST_MODELS_URL = f"{API_BASE}/{project_id}/list_models/"
try:
    resp = requests.get(LIST_MODELS_URL)
    resp.raise_for_status()
    models_list = resp.json()  # List of dicts with model_ID, model_name, metadata
except Exception as e:
    st.error(f"⚠️ Could not fetch models for project '{project_id}': {e}")
    st.stop()

if not models_list:
    st.warning(f"No models available for project '{project_id}'.")
    st.stop()

# --- Sidebar: Select Model ---
model_display = [f"{m['model_name']} ({m['model_ID']})" for m in models_list]
selected_index = st.sidebar.selectbox(
    "📂 Select a Model",
    range(len(models_list)),
    format_func=lambda i: model_display[i]
)
selected_model = models_list[selected_index]
model_id = selected_model["model_ID"]
model_name = selected_model["model_name"]

# --- Fetch metadata for selected model ---
METADATA_URL = f"{API_BASE}/{project_id}/metadata/{model_id}"
config = {}
try:
    resp = requests.get(METADATA_URL)
    resp.raise_for_status()
    config = resp.json()  # Full metadata
except requests.exceptions.RequestException as e:
    st.error(f"⚠️ Could not fetch metadata for '{model_name}': {e}")


# --- Main: Detailed Model View ---
st.markdown(f"<h3>🔍 Model Details: {model_name}</h3>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Overview", "Architecture", "Inputs", "Outputs", "Training Info", "Run Prediction"]
)

# --- Tab 1: Overview ---
with tab1:
    st.subheader("📌 Overview")
    st.write(config.get("model_description", {}).get("description", ""))
    st.write("Model Identification:")
    st.json(config.get("model_identification", {}))
    st.write("Programming Language:")
    st.json(config.get("model_description", {}).get("language", {}))
    st.write("Packages Used:")
    st.json(config.get("model_description", {}).get("packages", {}))
    st.write("Files:")
    st.json(config.get("model_description", {}).get("config_files", {}))

# --- Tab 2: Architecture ---
with tab2:
    st.subheader("⚙️ Architecture")
    arch = config.get("model_architecture")
    if arch:
        st.write("**Input Layer**")
        st.json(arch.get("input_layer", {}))
        if "lstm" in arch:
            st.write("**LSTM Layers**")
            st.json(arch["lstm"])
        if "layers" in arch:
            st.write("**Other Layers**")
            st.json(arch["layers"])
        st.write("**Output Layer**")
        st.json(arch.get("output_layer", {}))
    else:
        st.info("Architecture not defined for this model.")

# --- Tab 3: Inputs ---
with tab3:
    st.subheader("🔑 Inputs")
    inputs = config.get("inputs", {}).get("features", [])
    if inputs:
        st.dataframe(pd.DataFrame(inputs))
    else:
        st.info("No input features defined.")

# --- Tab 4: Outputs ---
with tab4:
    st.subheader("🎯 Outputs")
    outputs = config.get("outputs", {}).get("information", [])
    if outputs:
        st.dataframe(pd.DataFrame(outputs))
    else:
        st.info("No output predictions defined.")

# --- Tab 5: Training Info ---
with tab5:
    st.subheader("📊 Training Information")
    training = config.get("training_information", {})
    if training:
        st.write(f"Number of Instances: {training.get('number_of_instances', 'N/A')}")
        st.subheader("Hyperparameters")
        st.json(training.get("hyperparameters", {}))
        st.subheader("Validation Strategy")
        st.write(training.get("validation", "N/A"))
        st.subheader("Experiment IDs")
        st.write(training.get("experiments_ID", "N/A"))
    else:
        st.info("Training information not available.")

# --- Tab 6: Run Prediction ---
with tab6:
    st.subheader("🚀 Run Prediction")
    inputs = config.get("inputs", {}).get("features", [])
    if not inputs:
        st.info("No input features available for prediction.")
    else:
        with st.form("prediction_form"):
            st.write("Enter input values:")
            user_inputs = {}
            for feat in inputs:
                name = feat.get("name")
                dtype = feat.get("type", "float")
                unit = feat.get("units", "")
                description = feat.get("description", "")
                default_val = feat.get("default", 0)

                label = name
                if unit:
                    label += f" ({unit})"
                if description:
                    label += f" – {description}"

                if dtype == "int":
                    val = st.number_input(label, value=int(default_val))
                else:
                    val = st.number_input(label, value=float(default_val))

                user_inputs[name] = val

            submitted = st.form_submit_button("Predict")

        if submitted:
            PREDICT_URL = f"{API_BASE}/{project_id}/predict/{model_id}"
            payload = {"req": {"input_data": user_inputs}}
            try:
                resp = requests.post(
                    PREDICT_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=10
                )
                if resp.status_code == 200:
                    st.success("✅ Prediction successful!")
                    st.json(resp.json())
                else:
                    st.error(f"❌ Error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"Request failed: {e}")
