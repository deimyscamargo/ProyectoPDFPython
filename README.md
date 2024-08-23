•	RF2: Análisis y Extracción de texto
Los textos obtenidos de las imágenes deben ser procesados mediante inteligencia artificial de forma concurrente para obtener los siguientes datos:
•	Nombres de unidades militares (Batallones, Brigadas, Escuadrones, Fuerzas de Tarea)
•	Divisiones políticas mencionadas en el artículo (Departamentos, Ciudades, Municipios, Corregimientos, Veredas)
Además, se deben añadir los siguientes datos:
•	Fecha de publicación del artículo (extraída del nombre del archivo)
•	Nombre del periódico (extraído del nombre del archivo o de la carpeta que lo contiene)
•	Fecha de procesamiento en formato datetime
•	Tiempo de procesamiento
Todos estos datos deben ser almacenados en una base de datos.
•	RF3: Despliegue de Servicio
La aplicación debe ser montada y desplegada como un servicio web en un contenedor, ofreciendo las siguientes funcionalidades:
•	Mostrar el número de archivos procesados
•	Mostrar el tiempo promedio de procesamiento de archivos por el OCR
•	Mostrar el tiempo total de procesamiento de archivos por el OCR
•	Mostrar el tiempo promedio de procesamiento de archivos por la IA o procesamiento de lenguaje natural
•	Mostrar el tiempo total de procesamiento de archivos por la IA o procesamiento de lenguaje natural
•	Procesar archivos mediante OCR especificando el número de cores
•	Procesar texto con IA o procesamiento de lenguaje natural especificando el número de cores
