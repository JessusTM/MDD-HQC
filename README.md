# Model Driven Development for Hybrid Quantum-Classical Systems (MDD-HQC)

> **Version:** v1.1.0  
> **Status:** Functional Prototype

This repository contains a functional prototype for an agent-oriented MDD-based solution for creating hybrid quantum-classical systems. This solution enables the transformation of models built in iStar 2.0 to a structure and behavior level (PIM) through a feature model from the software product line domain for variability management, and finally, for the architectural modeling of a concrete system configuration.

This solution aims to achieve vertical traceability across the different levels of the HQC system, ensuring that elements are traceable and no information is lost.

> [!NOTE]
> The system enables the calculation of transformation metrics and the generation of class diagrams in PlantUML for platform-dependent designs.

## System Features

The following table shows the features currently implemented and those planned for future versions:

| Capability                                                             | Status |
| ---------------------------------------------------------------------- | ------ |
| **iStar 2.0 XML model upload**                                         | ✅     |
| **CIM metrics extraction (goals, tasks, softgoals, dependencies)**     | ✅     |
| **CIM → PIM transformation (iStar → UVL)**                             | ✅     |
| **UVL model generation (features, categories, OR-groups)**             | ⚠️     |
| **UVL metrics (categories, semantic preservation, constraints)**       | ⚠️     |
| **Preliminary PlantUML generation derived from UVL**                   | ⚠️     |
| **PSM metrics (classes, stereotypes, dependencies)**                   | ⚠️     |
| **Semi-automatic user–system interaction for completing missing model details across the entire pipeline (CIM → PIM → PSM)** | ❌ |
| **Conversational assistant for semantic interpretation of models**     | ❌     |
| **Semi-automatic support for enriching incomplete CIM/PIM information**| ❌     |
| **Automatic iStar model generation from repositories or local folders** | ❌    |
| **Expanded architectural templates for hybrid quantum–classical systems (SOA, middleware, integration patterns)** | ❌ |
| **Base code generation from the PSM architecture**                      | ❌     |


> [!CAUTION]
> Features marked with ❌ are planned for future versions and are not yet available in the current version.

## Technologies Used

### Backend
* **Python 3.x** - Main programming language
* **FastAPI** - Modern and fast web framework for building APIs
* **Uvicorn** - High-performance ASGI server
* **Pydantic** - Data validation and configuration using type annotations
* **PlantUML** - UML diagram generation from text

### Frontend
* **React 19** - JavaScript library for building user interfaces
* **React Scripts 5.0.1** - Configuration tools for React applications
* **Axios** - HTTP client for making requests to the backend
* **Lucide React** - Modern icon library
* **PlantUML Encoder** - PlantUML diagram encoding for visualization

### Infrastructure
* **Docker** - Application containerization
* **Docker Compose** - Multi-container service orchestration

## Prerequisites

The following must be installed before starting:

* Docker (version 20.10 or higher)
* Docker Compose (version 2.0 or higher)
* Git (for cloning the repository)

> [!NOTE]
> The system is designed to run in containerized environments using Docker Compose for optimal compatibility and ease of deployment.

## Installation and Execution

### Using Docker Compose

1. **Clone the repository:**
   ```bash
   git clone git@github.com:JessusTM/MDD-HQC.git
   cd MDD-HQC
   ```

2. **Build and start the services:**
   ```bash
   docker compose up --build
   ```

   This command builds the Docker images for the backend and frontend, and starts both services.

3. **Access the application:**
   * **Frontend:** [http://localhost:3000](http://localhost:3000)
   * **Backend API:** [http://localhost:8000](http://localhost:8000)
   * **API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Stop the services:**
   ```bash
   docker compose down
   ```

> [!CAUTION]
> Ensure that ports 3000 and 8000 are available on the system before running the containers. If these ports are in use, they can be modified in the `docker-compose.yml` file.

## Project Structure

### Backend (`mdd-hqc-backend`)

```
mdd-hqc-backend/
├── app/
│   ├── api/                          # API routes and controllers
│   │   └── file.py                      # Endpoints for XML file upload and processing
│   ├── data/                         # Example iStar 2.0 files in XML format
│   │   └── ChileEsPres.xml
│   ├── main.py                       # Main entry point of the FastAPI server
│   ├── models/                       # Data models and domain entities
│   │   ├── feature.py                  # UVL feature model
│   │   ├── uml.py                      # UML diagram model
│   │   └── uvl.py                      # UVL feature tree model
│   └── services/                     # Business logic and transformation services
│       ├── metrics/                     # Metrics calculation
│       │   ├── istar_metrics.py         # Metrics for iStar models
│       │   ├── plantuml_metrics.py      # Metrics for PlantUML diagrams
│       │   └── uvl_metrics.py           # Metrics for UVL models
│       ├── transformations/             # Transformations between model levels
│       │   ├── cim_to_pim.py            # CIM → PIM transformation
│       │   └── pim_to_psm.py            # PIM → PSM transformation
│       ├── plantuml_service.py          # Service for PlantUML diagram generation
│       ├── upload_service.py            # Service for handling uploaded files
│       ├── uvl_service.py               # Service for UVL model processing
│       ├── xml_service.py              # Service for processing XML diagrams
│       └── uvl_category_keywords.csv    # Keywords for UVL categorization
├── Dockerfile                        # Base image for backend deployment
└── requirements.txt                 # Python dependencies
```

### Frontend (`mdd-hqc-frontend`)

```
mdd-hqc-frontend/
├── public/
│   └── index.html                   # Root HTML file of the application
├── src/
│   ├── components/                  # Modular system components
│   │   ├── App.jsx                     # Main application component
│   │   ├── Commons/                    # Reusable common components
│   │   │   ├── Header.jsx              # Application header
│   │   │   └── MddCard.jsx            # Reusable card for displaying information
│   │   ├── Filter/                     # Filtering components
│   │   │   └── Filter.jsx              # Level filter for metrics panel
│   │   └── Levels/                    # Level visualization components
│   │       ├── CIM.jsx                 # CIM level (computation independent model)
│   │       ├── PIM.jsx                 # PIM level (platform independent model)
│   │       └── PSM.jsx                 # PSM level (platform specific model)
│   ├── services/                     # Backend communication services
│   │   └── api.js                      # API client for making HTTP requests
│   ├── index.js                      # React application entry point
│   └── style.css                     # Global application styles
├── Dockerfile                        # Base image for frontend deployment
├── package.json                      # Node.js project dependencies
└── package-lock.json                 # Dependency lock file
```

## Transformation Flow

The system implements a three-level transformation flow:

1. **CIM (Computation Independent Model)**: Computation-independent model based on iStar 2.0
2. **PIM (Platform Independent Model)**: Platform-independent model using UVL (Universal Variability Language)
3. **PSM (Platform Specific Model)**: Platform-dependent model with UML diagrams in PlantUML

> [!NOTE]
> Each transformation maintains traceability between levels, allowing elements to be traced from the business model to the platform-specific implementation.
