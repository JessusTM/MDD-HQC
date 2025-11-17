# Model-Driven Development for Hybrid Quantum–Classical Systems (MDD-HQC)

This repository contains a functional prototype of an **MDD-based solution** for engineering **Hybrid Quantum–Classical (HQC) systems**.  
The approach provides *vertical traceability* across three abstraction levels:

- **CIM** — Goal-oriented models using *iStar 2.0* in XML.  
- **PIM** — Variability models using *UVL* (feature models from Software Product Line Engineering).  
- **PSM** — Platform-specific architectural configurations for concrete HQC system instances.

The goal is to transform high-level goal models into structured representations that preserve information across levels, ensuring that decisions made at the CIM level remain traceable down to PIM and PSM.

The system currently offers:

- A **backend** for XML parsing, transformation logic, and UVL generation.  
- A **frontend** for interacting with models and exploring the CIM–PIM–PSM flow.  
- A **Docker-based** local environment for running the entire stack.

## ⚙️ Tech Stack

- **Python 3.12+**
- **FastAPI** with Uvicorn
- **React** (JavaScript, JSX components)
- **Docker & Docker Compose**
- **PlantUML** (planned integration for class diagram visualization)

## 🚀 Running the Project

1. Install **Docker** and **Docker Compose**.
2. Clone the repository:

```bash
git clone git@github.com:JessusTM/MDD-HQC.git
cd MDD-HQC
````

3. Build and start the services:

```bash
docker compose up --build
```

4. Access the frontend in your browser at: **[http://localhost:5173](http://localhost:5173)**

5. Stop the environment when you are done:

```bash
docker compose down
```

## 🧩 Project Structure

Global view of the repository, including orchestration, backend and frontend:

```text
.
├── docker-compose.yml          # Orchestration of backend and frontend services
├── mdd-hqc-backend/            # Backend service (FastAPI)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── data/               # Example iStar 2.0 XML models and sample UVL output
│       │   ├── Chemistry.xml
│       │   ├── ChileEsPres.xml
│       │   ├── ChileEsPresOLD.xml
│       │   └── model.uvl
│       ├── __init__.py
│       ├── main.py             # FastAPI entry point (ASGI application)
│       ├── models/
│       │   ├── __init__.py
│       │   └── uvl.py          # UVL-related data structures and helpers
│       └── services/
│           ├── __init__.py
│           ├── cli_service.py  # CLI utilities for local experimentation
│           ├── xml_service.py  # XML parsing and preprocessing for iStar 2.0 models
│           └── transformations/
│               ├── __init__.py
│               └── cim_to_pim.py  # Core CIM → PIM transformation logic
├── mdd-hqc-frontend/           # Frontend application (React)
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   │   ├── favicon.ico
│   │   └── index.html          # Root HTML for the SPA
│   └── src/
│       ├── components/
│       │   ├── App.jsx         # Root component of the UI
│       │   ├── Commons/
│       │   │   └── MddCard.jsx # Reusable card component for layout/sections
│       │   ├── Filter/
│       │   │   └── Filter.jsx  # Filter component for model/level selection
│       │   └── Levels/
│       │       ├── CIM.jsx     # CIM-level workspace (iStar 2.0 perspective)
│       │       ├── PIM.jsx     # PIM-level workspace (UVL / variability perspective)
│       │       └── PSM.jsx     # PSM-level workspace (platform-specific perspective)
│       ├── index.js            # React entry point (render root)
│       └── style.css           # Global styles for the application
└── README.md                   # Project documentation
```

## 📊 Current Capabilities

* Load and process **iStar 2.0 XML models** at the CIM level.
* Apply initial **CIM → PIM transformation rules** to generate UVL-based representations.
* Inspect and navigate **CIM, PIM, and PSM views** through the frontend.
* Run the entire system (backend + frontend) via a single **Docker Compose** configuration.

The prototype is intended as a research and experimentation platform for **Model-Driven Development in Hybrid Quantum–Classical Systems**, enabling further extensions such as refined transformation rules, metric extraction, and automated architectural views.
