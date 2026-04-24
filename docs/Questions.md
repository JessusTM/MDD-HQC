## Creación de un servicio de análisis de funciones del UVL

1. Se crea una función en uvl_service.py llamada extract_functionality_names que tiene como objetivo analizar la cantidad de subfunciones 
que están incluidas en una de las ramas del archivo UVL.

2. Se crea un endpoint de tipo POST en el archivo interactions.py que cumple con el rol de extraer el nombre de cada subfunción de las ramas
del archivo UVL cada vez que sea llamado por el usuario.

## Consumo de preguntas

1. Se crea un servicio de consumo de preguntas con JS en la carpeta src/services del frontend para conectarlo con el backend ocupando la 
librería Axios, hecha para el consumo API REST.

2. Se crea un archivo llamado Questions_modal en la carpeta src/components/Questions donde se deja creada una ventana modal para que el 
usuario pueda visualizar las preguntas junto con sus alternativas que le llegan en base a con qué tecnologías o frameworks desea trabajar 
en la propuesta de proyecto que envía a través de un modelo preliminar. 

3. Se conecta en el archivo App.jsx el modal de las preguntas junto con el servicio de consumo creado para que el usuario pueda visualizar
perfectamente desde la interfaz las preguntas y sus alternativas a escoger.