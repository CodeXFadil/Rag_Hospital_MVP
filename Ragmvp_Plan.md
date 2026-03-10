# Project: Multi-Agent Hospital Patient Records RAG Assistant

Build a complete prototype of a hospital patient-record AI assistant using a hybrid Retrieval Augmented Generation (RAG) architecture and multi-agent orchestration.

The system must allow users to query patient records in natural language and receive structured responses generated using both structured patient data and semantic retrieval of doctor notes.

The system should run locally, include a simple web UI, and be structured so that it can be stored and deployed from a GitHub repository.

---

# Core Architecture

Implement a hybrid retrieval system with both structured retrieval and semantic retrieval using RAG.

Architecture overview:

User Query  
↓  
Router Agent  
↓  
Structured Data Agent + Clinical Notes Retrieval Agent  
↓  
Clinical Reasoning Agent  
↓  
Coordinator Agent synthesizes the final response

The system should combine results from structured patient data and vector-based retrieval of doctor notes before sending context to the LLM.

---

# Multi-Agent Design

Create the following agents.

## Router Agent
Purpose: Determine user intent and route the query to the appropriate agents.

Possible query types include:

- patient data lookup
- medication queries
- lab result queries
- patient summary requests
- clinical notes search
- abnormal lab detection

The router should decide which agents to invoke based on the query.

---

## Patient Data Agent (Structured Retrieval)

Retrieve patient information from structured data stored in a CSV dataset.

Fields include:

- patient_id
- name
- age
- gender
- diagnoses
- medications
- lab_results
- visit_history

Use pandas to query the dataset.

---

## Clinical Notes Retrieval Agent (RAG)

Perform semantic retrieval over doctor notes.

Steps:

1. Convert doctor notes into document chunks.
2. Generate embeddings.
3. Store embeddings in a vector database.
4. Retrieve relevant notes using similarity search.

Use ChromaDB as the vector store.

Each chunk must include the patient_id to prevent mixing patient data.

---

## Clinical Reasoning Agent

Analyze retrieved patient data and highlight potential clinical concerns.

Example rules:

- HbA1c greater than 7 indicates uncontrolled diabetes.
- Systolic blood pressure greater than 140 indicates hypertension risk.
- Elevated cholesterol may indicate cardiovascular risk.

This agent must only reason over retrieved information and must never fabricate patient data.

---

## Coordinator Agent

This agent orchestrates the workflow.

Responsibilities:

- receive the user query
- invoke the necessary agents
- gather outputs from each agent
- synthesize a final response using the LLM

---

# Data Layer

Generate a synthetic dataset containing at least 50 patient records.

Each patient record must contain:

- patient_id
- name
- age
- gender
- diagnoses
- medications
- lab_results
- doctor_notes

Store structured fields in:

data/patients.csv

Doctor notes should be processed into vector embeddings for semantic retrieval.

---

# LLM Integration

Use OpenRouter API for LLM access.

Configuration:

OpenRouter endpoint using OpenAI compatible format.

Default model:

meta-llama/llama-3-8b-instruct

Set temperature to 0 to reduce hallucinations and improve factual responses.

The API key must be loaded from environment variables.

Example environment variable:

OPENROUTER_API_KEY=your_api_key_here

Do not hardcode API keys in the code.

---

# RAG Pipeline

Implement the following pipeline:

Patient dataset  
↓  
Document conversion  
↓  
Text chunking  
↓  
Embeddings generation  
↓  
Chroma vector database storage  
↓  
Retriever  
↓  
LLM response generation

Ensure relevant patient context is retrieved before generating responses.

---

# User Interface

Create a simple web UI using Streamlit that runs locally.

The UI should include:

Title: "Hospital Patient Records Assistant"

Components:

- text input field for user queries
- submit button
- response display area
- patient summary section

The output should present structured sections including:

Patient Overview  
Current Medications  
Recent Lab Results  
Clinical Notes Summary  
Risk Indicators

---

# Example Queries

The system must handle queries such as:

"What medication is Rahul Sharma taking?"

"Summarize patient P014."

"Which patients have HbA1c above 8?"

"What concerns appear in this patient's doctor notes?"

---

# Project Structure

Generate the following project structure:

hospital_rag_project/

data/  
patients.csv  

agents/  
router_agent.py  
patient_data_agent.py  
notes_agent.py  
clinical_reasoning_agent.py  
coordinator_agent.py  

rag/  
vector_store.py  
retriever.py  

ui/  
app.py  

requirements.txt  
README.md  

---

# Git Integration

Initialize Git version control for the project.

Steps:

1. Initialize a git repository.
2. Create a .gitignore file.
3. Exclude the following files and directories:

.env  
__pycache__/  
*.pyc  
vector_db/  

4. Prepare the project for GitHub integration so the codebase can be pushed directly to GitHub.

The README.md should contain instructions for:

- installing dependencies
- running the Streamlit application
- configuring the OpenRouter API key

---

# Installation

Dependencies should be installable using:

pip install -r requirements.txt

---

# Running the Application

The application should run locally using:

streamlit run ui/app.py

The UI should open in a browser at:

http://localhost:8501

---

# Goal

Deliver a working prototype of a multi-agent hospital patient records AI assistant demonstrating:

- hybrid RAG retrieval
- multi-agent orchestration
- patient data querying
- clinical reasoning
- local Streamlit UI
- GitHub-ready repository structure