# Memoria a demanda entre sesiones de Claude Code

## Problema

Al abrir una sesión nueva, el agente no tiene acceso a lo que se hizo en sesiones anteriores. Dentro de una misma sesión todo funciona bien.

## Opciones descartadas

Todas las opciones que cargan contexto al inicio se descartaron porque consumen contexto desde el primer mensaje, aunque no se necesite:

- CLAUDE.md con historial o decisiones acumuladas.
- Memoria automática en archivos, que se carga al inicio.
- Notas de sesión importadas desde CLAUDE.md.
- Retomar sesiones con `claude --continue` o `claude --resume`, porque solo recupera una conversación completa y no permite consultar varias sesiones antiguas desde una nueva.

## Enfoque elegido

Recuperación bajo demanda. Un script de búsqueda local indexa las transcripciones de Claude Code, que se guardan como archivos JSONL en `%USERPROFILE%\.claude\projects\`. Cuando el usuario pregunta por trabajo anterior, el agente ejecuta el script con la herramienta Bash, obtiene los fragmentos relevantes con fecha y sesión, y los usa para responder.

Costo al inicio: cero, porque el script no se carga en el contexto hasta que se usa. Solo se agrega una línea en CLAUDE.md que indique cuándo usarlo.

## Pendientes antes de construirlo

1. Confirmar el formato exacto de los JSONL en este equipo, porque la ruta y la estructura pueden cambiar según la versión de Claude Code.
2. Validar con la política de datos de Improving si indexar transcripciones es aceptable. Si las sesiones contienen datos de clientes, credenciales, PII o material criptográfico, deben revisarse o anonimizarse antes de procesarlas con IA. El índice se queda en la máquina, pero la política aplica al contenido.
3. Definir el lenguaje del script (PowerShell o Python) según lo que esté instalado.

## Estado del proyecto

- La carpeta del proyecto cambió de `engram-agm` a `brain-agm`.
- La sesión actual trabaja en `C:\ai_projects\brain-agm`, y su transcripción está en `%USERPROFILE%\.claude\projects\C--ai-projects-brain-agm\`.
- Pendiente: eliminar la carpeta vacía `C:\ai_projects\engram-agm` y la copia anterior de la sesión en `%USERPROFILE%\.claude\projects\C--ai-projects-engram-agm\`. La herramienta bloqueó el borrado, así que debe hacerse manualmente.


## Plan para crear la herramienta de memoria global
 ok, esto es lo que quiero:

  La idea es compartir memoria de una sesión a otra entre diferentes IDEs o CLIs, para eos quiero que dentro de una sesión que el agente sea capaz de: que si se hizo un plan se ejecutó o se cerró el plan se guarde en memoria. Quiero también que cuando se tomen
  decisiones importantes se guarden en memoria, con el por qué y el para qué. Quiero que cuando el agente al trabajar y encuentre algun problema y tome una decisión importante, también que la guarde en memoria, y si yo como usuario le digo explicitamente que lo guarde
  en memoria, que también lo haga y que cada 15min el agente se pregunte así mismo si hay algo nuevo que se deba guardar. Además quiero que se puedan actualizar las memorias guardadas, por si un plan o decisión cambió que se actualice.

  La estructura de como quiero que se guarde que sea la siguiente:
  - Que en todas las computadoras con Windows o MAC se cree un folder llamado brain-agm en documentos, donde se almacenarán todas las memorias (el location puede ser cualquiera, pero que sea una ruta que siempre exista y que se pueda crear siempre el folder brain-agm,
  recomiendame el mejor lugar para cada OS).
  - Al abrir una sesión de chat con cualquier agente brain-agm debe crear un folder dentro de brain-agm con el nombre del proyecto en el que estamos trabajando y el nombre de debe tomar del nombre de la carpeta en donde estamos parados.
  - Dentro de un proyecto se deben guardar todas sus memorias con un título, la fecha, y en el siguiente formato:
  a) Breve descripción, b) El qué y el por qué

  En una sesión de chat el agente debe ser capaz de detectar que el usuario hace una pregunta y si la pregunta da a entender que es algo que se trabajó anteriormente o hubo una decisión importante que se tomó y que pueda existir en la memoria de brain-agm el agente
  debe ir a buscar algo en memoria relacionado y si está relacionado que lo cargue en el contexto de la actual conversación y que le muestre al usuario lo que encontró. Importante hacer la referencia de la memoria que se recuperó. El usuario puede pedir explicitamente
  que se busque algo en memoria del proyecto o incluso de otro proyecto.

  No soy una persona muy técnica, por lo que quiero mantener lo más simple posible esta herramienta pero quiero que funcione global en mi máquina para cualquier proyecto o sesión que yo abra. Quiero que funcione para Claude y para Devin/Windsur. En este momento me
  puedo imaginar que podemos crear para claude un archivo claude.md que referencie a agents.md donde se defina esta herramienta como funciona y para qué y para que el agente al iniciar la sesión conozca que existe la herramienta y para que sepa como usarla y cuando.
  Además quizás habrá que crear un skill o mcp para hacer la lectura o el guardado, y los mismos archivos habrá que crearlos para devin/windsurf.

  Todos los archivos de este proyecto guardalos en esta carpeta: C:\AI_Projects\brain-agm porque quiero poder compartirlo con otros compañeros y que lo instalen por si les sirve. Por lo que quiero tener un script que ayude en la instalación y configuración de la herramienta. Y otro scrípt para remover la herramienta y recuerda mantener esto lo más simple posible.

----------

  El Agents.md si puede ir global en cada carpeta de configuración del IDE, al mismo nivel que claude.md por ejemplo. Solo recuerda que claude tiene que referenciar a agents.md.

  No quiero que utilices mecanismos específicos de un ide para guardar memorias, quiero que sea un mecanismo simple que funcione en cualquier ide y que las memorias se guarden en la carpeta que te indiqué, pero si puedes tomar ideas de funcionalidades que ya existan.

  Sí hay skills globales para claude, investigalo.