## Módulo de Interacción Semi-Automática

Este módulo dentro del sistema aparece **cuando el sistema ya leyó el modelo iStar (XML) y antes de escribir el UVL final**. En particular, el sistema a día de hoy sigue el siguiente flujo:

1. **Se sube un archivo XML** (iStar 2.0).
2. El backend **lee el XML** y extrae información:

   * una lista de **nodos** (goals, tasks, softgoals, recursos, actores, etc.);
   * una lista de **enlaces** (dependencias sociales, needed-by, qualification, contributions, refinements).
3. Con esa información, el backend aplica reglas de transformación y construye un **UVL**.

Aquí, el módulo se coloca **entre el paso 2 y el paso 3**:

* **Después** de extraer nodos y enlaces desde el XML (ya están en estructuras de datos simples).
* **Antes** de consolidar el UVL final (antes de escribirlo como archivo definitivo).

##### Necesidad

Este componente debe permitir **interactuar con el usuario** cuando el sistema necesita ayuda para completar o validar el modelo, ya que se reconoce que **las reglas automáticas no siempre son suficientes ni garantizan capturar la totalidad de la información**. Por ejemplo:

* puede existir una característica ubicada en una sección que no corresponde a su naturaleza; por ejemplo, que sea un *algoritmo* pero haya sido ubicada en *funcionalidad*;
* pueden existir características que no hayan sido abordadas en el modelo, por lo que se debe preguntar al usuario por la característica correspondiente;
* se deben proponer correcciones que el usuario pueda aceptar o editar.

Con esto, este módulo existe para *hacer preguntas y proponer ajustes* en vez de que el sistema *asuma cosas incorrectas* o *produzca un UVL final incompleto*.

---
## Qué se espera del módulo

Cuando el módulo de interacción con el usuario aparezca en el flujo CIM-PIM, este no debe producir un archivo nuevo ni cambiar el flujo, solo debe producir un **reporte de apoyo** para el usuario, con dos partes:

##### 1) Preguntas

Son preguntas que el sistema debería mostrar al usuario cuando:

* falta información necesaria para una decisión;
* hay ambigüedad y se requiere confirmar;
* se detecta que un dato no calza con el borrador UVL.

Estas preguntas deben ser:

* específicas (no abiertas en exceso);
* fáciles de responder;
* relacionadas con los datos del modelo.

> Ejemplo:
>
> * *Este elemento parece un algoritmo: ¿se clasifica como @Algorithm o como @Functionality?*
> * *Se detectó integración, pero falta método: ¿API, middleware, microservicio u otro?*

##### 2) Propuestas

Son sugerencias de cambios concretos sobre el UVL preliminar, por ejemplo:

* mover una feature a otra categoría;
* agregar un atributo derivado de un softgoal;
* agregar una constraint a partir de una dependencia;
* agregar un hijo a un OR-group;
* agregar un comentario para preservar semántica.

> Importante: las propuestas **no se aplican automáticamente**. El usuario decide.

##### LLM como apoyo y no como caja negra

Para este punto se considera que la presencia del LLM es únicamente para **apoyar la interpretación semántica** del modelo, principalmente mediante la **redacción de preguntas** y la **formulación de propuestas**. En particular:

* El LLM cumple un rol **asistivo** dentro del flujo, no un rol de **decisión**: no controla el flujo ni aplica cambios de forma autónoma.
* El LLM procesa solo información **estructurada y verificable** que el sistema le entrega, conforme a un **contrato de entrada/salida** previamente definido.
* El LLM **no debe** introducir información ajena al input ni realizar inferencias no sustentadas; ante ambigüedad o faltantes, debe expresarlo mediante **preguntas**.
* Bajo este enfoque, el LLM no actúa como una *caja negra*, sino como un componente de apoyo que complementa la capacidad de un enfoque puramente determinista para capturar matices semánticos.

---
## Formas de interacción: *rule_based* y *llm_based* (polimorfismo)

Para apoyar la interacción con el usuario durante la etapa **CIM → PIM**, el sistema contempla dos formas de ejecución, ambas con el mismo fin: **obtener un UVL preliminar más completo y coherente**, sin perder trazabilidad respecto de lo que realmente estaba en el modelo iStar 2.0.

##### 1) *llm_based* (asistencia semántica)

* Usa un modelo LLM como **apoyo para interpretar la semántica** de los elementos que componen el modelo de la etapa CIM y cómo deberían reflejarse en UVL.
* Su aporte principal es mejorar la calidad de la interacción con el usuario, generando:

  * **preguntas** más claras cuando detecta ambigüedad o información faltante;
  * **propuestas** mejor justificadas para ajustar el UVL preliminar (por ejemplo, mover una feature de categoría o sugerir atributos/constraints).

> Importante: el LLM **no decide por el sistema**. No controla el flujo ni aplica cambios automáticamente. Trabaja únicamente con la información estructurada que el sistema le entrega (nodos/enlaces + borrador UVL) y produce un reporte para que el usuario confirme.

##### 2) *rule_based* (determinista, sin semántica avanzada)

* No usa LLM. Se basa en reglas explícitas y verificaciones directas.
* Su objetivo es guiar al usuario para que confirme lo que el sistema no puede determinar con certeza solo con reglas, por ejemplo:

  * dónde ubicar un elemento del CIM dentro de las categorías UVL;
  * qué atributo corresponde a un softgoal;
  * si una relación debe traducirse a una constraint u OR-group.
* Suele requerir más confirmaciones manuales, por lo que puede ser **más lento** que *llm_based*. A cambio, es totalmente reproducible y funciona siempre, incluso sin credenciales para LLM.

> Nota: *llm_based* tiende a acelerar la interacción y reducir preguntas innecesarias gracias a mejor interpretación semántica. *rule_based* prioriza reproducibilidad y disponibilidad sin dependencias externas.

---
## Contrato común de ejecución (*InteractionEngine*)

Para que el sistema pueda usar cualquiera de los dos motores sin reescribir el pipeline, ambos deben cumplir un **mismo contrato de ejecución**, definido en:

* Archivo: `app/services/interaction/interaction_engine.py`
* Interfaz: `InteractionEngine`

Este contrato define una regla simple y estable: **cómo se llama al motor y qué debe devolver**.

* Existe un único método esperado: `run(payload) -> InteractionReport`.
* `payload` es un `InteractionInput`, que contiene exactamente lo necesario para entender el caso:

  * **evidencia del CIM** ya extraída por el sistema (nodos y enlaces);
  * **UVL preliminar** (borrador del PIM en memoria, antes de escribir el archivo final).
* El retorno es siempre un `InteractionReport`, que resume qué se debe consultar o sugerir al usuario:

  * `questions`: preguntas para completar o aclarar información;
  * `proposals`: propuestas de cambios sobre el UVL preliminar, con justificación.

La ventaja de respetar este contrato es que ambos motores terminan **hablando el mismo idioma** hacia el resto del sistema: entregan la misma forma de entrada y salida, y exponen el mismo método `run(...)`.

Esto habilita **polimorfismo**:

* el pipeline no necesita saber si el motor real es *rule_based* o *llm_based*;
* el pipeline solo conoce la interfaz `InteractionEngine`;
* mientras exista `run(...)` con el mismo contrato, el motor puede intercambiarse sin afectar el resto.

En otras palabras: el pipeline **no consume detalles internos** del motor; consume solo el contrato.

---
## Contratos del sistema: por qué existen y cómo se separan

Para mantener bajo acoplamiento y permitir reemplazar componentes sin romper el sistema, se separan dos tipos de acuerdos:

1. un acuerdo sobre **cómo se representan los datos** (qué campos existen y qué significan);
2. un acuerdo sobre **cómo se ejecuta la interacción** (qué método se llama y qué se devuelve).

Esta separación es intencional: evita que la lógica del pipeline dependa de detalles particulares de un motor, de una librería o de un proveedor LLM.

##### 1) Contrato de datos (DTO)

Este contrato define estructuras claras y estables para representar:

* el CIM ya extraído desde iStar (nodos y enlaces);
* el UVL preliminar (features, constraints, OR-groups);
* el resultado de Interaction (preguntas y propuestas).

Su objetivo es que cualquier motor (rule-based o LLM) reciba **los mismos datos**, en el mismo formato, y devuelva resultados comparables.

* Archivo: `app/models/llm_contract.py`

##### 2) Contrato de ejecución (interfaz)

Este contrato define **cómo se invoca** cualquier motor de interacción, sin importar su implementación interna.

* El pipeline llama siempre al mismo método (`run(...)`).
* El pipeline recibe siempre el mismo tipo de salida (`InteractionReport`).
* El motor puede cambiar internamente (reglas nuevas, otro LLM, otro proveedor) sin exigir cambios en el pipeline, mientras respete el contrato.

- Archivo: `app/services/interaction/interaction_engine.py`
- Requisito: cualquier motor debe exponer `run(input) -> report` conforme al contrato de datos.

---
## Regla operativa de selección (fallback):

* Si no existe API_KEY (o está vacía) ⇒ el sistema utiliza rule_based de inmediato.
* Si existe API_KEY ⇒ el sistema puede utilizar llm.
* En ambos casos, el pipeline ejecuta exactamente el mismo patrón: engine.run(input).

---
## Idea de Estructura para el Módulo

Organización sugerida para mantener el componente de interacción **separado**, **intercambiable** (LLM vs reglas) y con dependencias estables basadas en **contratos**. No es obligatorio copiarla exacta, pero es una base.

```
mdd-hqc-backend/
└── app/
    ├── models/
    │   └── llm_contract.py
    └── services/
        └── interaction/
            ├── __init__.py
            ├── interaction_engine.py
            ├── rule_based.py
            ├── llm.py
            └── service.py
```

* `app/models/llm_contract.py`: DTOs de entrada/salida (CIM + UVL preliminar + reporte).
* `app/services/interaction/interaction_engine.py`: interfaz `InteractionEngine` (`run(...) -> InteractionReport`).
* `app/services/interaction/rule_based.py`: motor determinista (reglas/heurísticas) que genera preguntas/propuestas.
* `app/services/interaction/llm.py`: motor con LLM que genera preguntas/propuestas con apoyo semántico.
* `app/services/interaction/service.py`: punto único de integración; selecciona motor (API_KEY → LLM, si no → reglas).
* `app/services/interaction/__init__.py`: paquete (puede estar vacío).
