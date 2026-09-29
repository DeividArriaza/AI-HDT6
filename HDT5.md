Objetivos
Familiarizarse con sistemas multiagentes (MAS) orquestrados de manera jerárquica, centralizada y decentralizada.
Instrucciones
Resuelvan el siguiente problema utilizando las arquitecturas de orquestación centralizada, jerárquica y decentralizada.

Si ustedes utilizan el SDK de OpenAI, para la arquitectura centralizada y jerárquica puede utilizar la función de as_tool() para crear los agentes  supervisor/manager. Para la arquitectura decentralizada puede utilizar el parámetro de handoff de un agente.

Debe de entregar 3 programas en un repositorio en conjunto con un diagrama de como quedaron organizados sus agentes en cada arquitectura, cada uno resolviendo el mismo problema con una arquitectura distinta, en conjunto con un PDF con las respuestas a las preguntas planteadas en el problema.

Problema
Parachute S.A le gustó mucho su trabajo realizado, por lo que ahora le ha pedido los siguientes nuevos requerimientos funcionales adicionales a los ya realizados con la base de conocimientos de FAQs:

Desean que el agente ahora pueda calendarizar citas chequeando el clima antes. Esto lo debe lograr consultando la API gratuita de Open-Meteo  para la fecha que el usuario desea, los parámetros de búsqueda son los siguientes:
Coordenadas del lugar de aterrizaje: 14.013722, -90.771611
Fecha que el usuario desea calendarizar cita (Open Meteo unicamente provee hasta 16 días de predicción), si el usuario pide la fecha despues de 16 días se le debe corregir que no se puede.
Para la API de open meteo utiliza la opción de current o daily.
Tiene que obtener los valores de ráfaga de viento (wind_gust_10m), temperatura (temperature_2m), precipitación (precipitation), visibilidad (cloud_cover) y velocidad de viento superficie (wind_speed_10m) 
Una vez cuente con esta información el critero para aceptar si el día es bueno para saltar es el siguiente:
Velocidad del viento en superficie:
Ideal: < 20 km/h

Marginal (Solo tándem experimentado): 20–28 km/h

NO SEGURO / PROHIBIDO: > 28 km/h (Muy díficil de controlar el salto)

Ráfagas de viento
NO SEGURO / PROHIBIDO: > 35 km/h
Precipitación:
NO SEGURO / PROHIBIDO: > 0.0 mm (Saltar con lluvia daña el equipo y lastima la piel)
Cobertura de nubes / Visibilidad:
Ideal: < 30% (Visibilidad clara)

Marginal: 30 - 75% (Nubes dispersas)

NO SEGURO / PROHIBIDO: > 75% (Un techo de nubes bajo impide las reglas de vuelo visual)

Parachute S.A le ha advertido que va a seguir incrementando los requerimientos funcionales
Se le recomienda que realice las abstracciones necesarias para que sea facil realizar la implementación de las 3 arquitecturas sin cambiar la lógica de las integraciones.
 

Preguntas

¿Qué arquitectura/arquitecturas resuelven mejor este problema? ¿Por qué?
¿Considera que es necesario utilizar un sistema multiagente en este caso? ¿Por qué?
