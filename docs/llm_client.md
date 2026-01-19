## Configuración del cliente LLM (Ollama y/o LMStudio)

En este apartado se explica la configuración realizada con los clientes LLM desde las plataformas Ollama y LMStudio

1. Se crea un archivo llamado ollama_client.py en el directorio /mdd-hqc-backend/app/services/llm/ donde se define la lógica de funcionamiento del modelo LLM a través de funciones donde se configura la creación de prompts para analizar los elementos iStar que contenga un archivo XML y entregar como resultado los elementos hallados y algún tipo de ambigúedad detectada si es que es el caso.

2. Se crea un archivo llamado lmstudio_client.py en el directorio mdd-hqc-backend/app/services/llm/ donde se define una lógica similar a la definida en ollama_client.py, aquí también se construye un prompt para darle instrucciones al LLM acerca de lo que debe analizar en un archivo XML.

3. Se crea un archivo llm.py en el directorio mdd-hqc-backend/app/services/interaction que define la lógica de como el LLM tendría que ir generando las preguntas en base a los elementos iStar encontrados durante el análisis del archivo XML.

4. Se crea un archivo rule_based.py que cumple rol de manejar la lógica de una interacción con un motor determinista alternativo que está basado en reglas específicas para detectar durante el análisis que elementos estarían faltando dentro de un archivo o si es que hay algún tipo de ambigüedad en algún elemento presente.

5. Se crea un archivo service.py en el directorio mdd-hqc-backend/app/services/interaction en el cual se obtiene el cliente LLM que se va a utilizar para la ejecución del modelo en el sistema, este cliente es escogido antes de la ejecución incluyendo entre las opciones el motor determinista basado en reglas específicas.

## Decisiones Tomadas

1. Tener creado un motor determinista rule-based como respaldo para validar modelos o partes de ellos sin depender de IA.

2. Dejar definido un cliente LLM por defecto como parámetro con el fin de simplificar pruebas que se realizan al sistema.


## Herramientas/Servicios utilizados

- Ollama (Llama 3.1)
- LMStudio (Meta llama 3.8)
- FastAPI (Python)
- React