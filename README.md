# Model Driven Development for Hybrid Quantum-Hybrid Systems

Este repositorio contiene un protótipo funcional para una solución basada en MDD orientada a agentes para la creación de sistemas híbridos. Con esta, se permite transformar modelos construídos en iStar 2.0, a un nivel de estructura y comportamiento (PIM) por medio de un modelo de característica del dominio de las líneas de producto de software para la gestión de variabilidad y, finalmente, para el modelado arquitectónico de una configuración concreta del sistema. Con esta solución se busca obtener una trazabilidad vertical en los diferentes niveles del sistema HQC, de manera que sean trazables y no exista pérdida de información.

El sistema permite el cálculo de métricas de transformación y la generación de diagramas de clases en PlantUML para los diseños dependientes de la plataforma. Como stack tecnológico se hace uso del lenguaje **Python** como backend junto al framework **FastAPI** y un frontend con lenguaje **Typescript** desarrollado en la librería **React**.

## Tecnologías utilizadas

* Python 3.14
* FastAPI con Uvicorn
* Pydantic para validación de datos
* React 19 con Vite y TypeScript
* Docker y Docker Compose para la orquestación local
* PlantUML para la visualización de diagramas de clases generados

## Pasos de ejecución

1. Instalar Docker y Docker Compose.
2. Clonar el repositorio:

   ```bash
   git clone git@github.com:JessusTM/MDD-HQC.git
   cd RDD-Hybrid-Systems
   ```
3. Construir y levantar los servicios:

   ```bash
   docker compose up --build
   ```
4. Acceder al entorno del frontend en:
   **[http://localhost:5173](http://localhost:5173)**
5. Detener el entorno al finalizar:

   ```bash
   docker compose down
   ```

---

## Estructura del proyecto

### Backend (`mdd-hqc-backend`)

```
.
├── app
│   ├── api                         # Rutas y controladores de la API
│   │   ├── transformations.py         # Endpoints para las transformaciones CIM–PIM–PSM
│   │   └── xml.py                     # Endpoints de carga y procesamiento de archivos XML
│   ├── core                        # Configuración base del sistema
│   │   ├── config.py                  # Variables de entorno y parámetros globales
│   │   └── logging.py                 # Configuración de registro y logs
│   ├── data                        # Ejemplos iStar 2.0 en formato XML para el primer nivel de modelado
│   │   │   ├── Chemistry.xml
│   │   │   └── ChileEsPres.xml
│   ├── main.py                     # Punto de entrada principal del servidor FastAPI
│   ├── models                      # Modelos de datos y entidades del dominio
│   │   ├── feature_tree.py            # Representación de árboles de características UVL
│   │   ├── metrics.py                 # Estructuras de métricas calculadas
│   │   ├── transformation_result.py   # Resultados intermedios y finales de las transformaciones
│   │   └── xml.py                     # Modelo para manejo de archivos XML
│   └── services                    # Servicios auxiliares de negocio y transformación
│       ├── cli_args_service.py        # Módulo para argumentos de línea de comandos
│       ├── xml_service.py             # Servicio para procesar diagramas XML
│       └── transformations            # Transformaciones entre niveles del modelo
│           ├── cim_to_pim.py
│           ├── pim_to_psm.py
│           ├── metrics_calculator.py
│           └── plant_uml_diagram_service.py
├── Dockerfile                      # Imagen base para despliegue del backend
├── requirements.txt                # Dependencias de Python
└── tests
```

---

### Frontend (`mdd-hqc-frontend`)

```
.
├── public
│   └── vite.svg                 
├── src
│   ├── assets                   
│   │   └── react.svg
│   ├── components               # Componentes modulares del sistema
│   │   ├── Filters
│   │   │   └── LevelFilter.tsx  # Filtro de niveles para el panel de métricas
│   │   ├── Layout
│   │   │   └── Layout.tsx       # Estructura principal del layout
│   │   ├── Levels
│   │   │   ├── CimLevel.tsx     # Nivel CIM (modelo independiente del cómputo)
│   │   │   ├── PimLevel.tsx     # Nivel PIM (modelo independiente de la plataforma)
│   │   │   └── PsmLevel.tsx     # Nivel PSM (modelo dependiente de la plataforma)
│   │   ├── Metrics
│   │   │   └── MetricsPanel.tsx # Panel de visualización de métricas
│   │   └── Orchestrator
│   │       └── Orchestrator.tsx # Orquestador de transformaciones y vistas
│   ├── index.css                # Estilos globales
│   ├── main.tsx                 # Punto de entrada de la aplicación React
│   ├── services                 # Servicios de comunicación con el backend
│   │   ├── CimService.ts
│   │   └── PimService.ts
│   ├── types                    # Definiciones de tipos TypeScript
│   │   ├── components
│   │   │   ├── filters.ts
│   │   │   └── levels.ts
│   │   ├── levels.ts
│   │   ├── metrics.ts
│   │   └── transformations.ts
│   └── utils
│       └── uvl.ts               # Funciones auxiliares para manejo de UVL
├── Dockerfile                   # Imagen base para despliegue del frontend
├── eslint.config.js             # Configuración de reglas de linting
├── index.html                   # Archivo raíz de la aplicación
├── package.json                 # Dependencias del proyecto Node.js
├── package-lock.json
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts               # Configuración de Vite para desarrollo y compilación
```
