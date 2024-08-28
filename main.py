import os
import pytesseract
from pdf2image import convert_from_path
from concurrent.futures import ProcessPoolExecutor, as_completed
import datetime
import sqlite3

# Configurar la ruta al ejecutable de Tesseract
#Apytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Registrar los adaptadores para datetime
sqlite3.register_adapter(datetime.datetime, lambda dt: dt.isoformat())
sqlite3.register_converter("DATETIME", lambda s: datetime.datetime.fromisoformat(s.decode()))

# Función para crear las tablas si no existen
def crear_tablas():
    """Crea las tablas 'procesamiento_pdf' y 'resumen_procesamiento' en la bd"""
    db_path = 'procesamiento_pdfs.db'
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Tabla para detalles del procesamiento de cada PDF
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS procesamiento_pdf (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_procesamiento DATETIME,
            ruta_archivo TEXT,
            nombre_archivo TEXT,
            texto_extraido TEXT,
            tiempo_procesamiento REAL
        )
    ''')

    # Tabla para almacenar el resumen del procesamiento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumen_procesamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_resumen DATETIME,
            tiempo_total_procesamiento REAL,
            numero_total_archivos INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Las tablas de la base de datos se están guardando en: {os.path.abspath(db_path)}")

# Función para extraer texto de un PDF y almacenarlo en la base de datos
def extraer_texto_y_guardar(pdf_path, ocr_language='spa'):
    """
    Extrae el texto de un archivo PDF utilizando OCR y guarda el texto extraído junto con
    los detalles del procesamiento en la base de datos.

    Args:
        pdf_path (str): Ruta del archivo PDF.
        ocr_language (str): Código de idioma para OCR (por defecto 'spa' para español).

    Returns:
        float: Tiempo de procesamiento del archivo PDF en segundos.
    """
    start_time = datetime.datetime.now()  # Tiempo de inicio del procesamiento
    imagenes = convert_from_path(pdf_path)  # Convertir cada página del PDF a una imagen
    texto_total = ""
    for num_pagina, imagen in enumerate(imagenes):
        # Extraer texto de la imagen utilizando Tesseract OCR
        texto_extraido = pytesseract.image_to_string(imagen, lang=ocr_language)
        texto_total += f"\n--- Página {num_pagina + 1} ---\n"  # Agregar un encabezado de página
        texto_total += texto_extraido  # Agregar el texto extraído a la variable total
    end_time = datetime.datetime.now()  # Tiempo de finalización del procesamiento
    tiempo_procesamiento = (end_time - start_time).total_seconds()  # Calcular el tiempo de procesamiento
    
    # Guardar los detalles del procesamiento en la base de datos
    guardar_en_base_de_datos(pdf_path, texto_total, tiempo_procesamiento)
    
    return tiempo_procesamiento

# Función para guardar en la base de datos SQLite
def guardar_en_base_de_datos(pdf_path, texto_extraido, tiempo_procesamiento):
    """
    Guarda los detalles del procesamiento de un archivo PDF en la base de datos SQLite.

    Args:
        pdf_path (str): Ruta del archivo PDF.
        texto_extraido (str): Texto extraído del PDF.
        tiempo_procesamiento (float): Tiempo de procesamiento del PDF en segundos.
    """
    conn = sqlite3.connect('procesamiento_pdfs.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    nombre_archivo = os.path.basename(pdf_path)  # Obtener el nombre del archivo
    fecha_procesamiento = datetime.datetime.now()  # Obtener la fecha y hora actual para el registro
    cursor.execute('INSERT INTO procesamiento_pdf (fecha_procesamiento, ruta_archivo, nombre_archivo, texto_extraido, tiempo_procesamiento) VALUES (?, ?, ?, ?, ?)',
            (fecha_procesamiento, pdf_path, nombre_archivo, texto_extraido, tiempo_procesamiento))
    conn.commit()
    conn.close()

# Función para guardar el resumen del procesamiento
def guardar_resumen_procesamiento(tiempo_total, numero_total_archivos):
    """
    Guarda un resumen del procesamiento de archivos PDF en la base de datos SQLite.

    Args:
        tiempo_total (float): Tiempo total de procesamiento de todos los archivos en segundos.
        numero_total_archivos (int): Número total de archivos procesados.
    """
    conn = sqlite3.connect('procesamiento_pdfs.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    fecha_resumen = datetime.datetime.now()  # Obtener la fecha y hora actual para el resumen
    cursor.execute('INSERT INTO resumen_procesamiento (fecha_resumen, tiempo_total_procesamiento, numero_total_archivos) VALUES (?, ?, ?)',
            (fecha_resumen, tiempo_total, numero_total_archivos))
    conn.commit()
    conn.close()

# Función para procesar PDFs en un directorio recursivamente
def procesar_pdfs_en_directorio_recursivo(pdf_directory, num_cores):
    """
    Procesa todos los archivos PDF en un directorio y sus subdirectorios de forma concurrente,
    utilizando un número especificado de núcleos de CPU.

    Args:
        pdf_directory (str): Directorio raíz donde buscar archivos PDF.
        num_cores (int): Número de núcleos de CPU a utilizar para el procesamiento concurrente.
    """
    tiempo_total = 0  # Inicializar el tiempo total de procesamiento
    numero_total_archivos = 0  # Inicializar el número total de archivos procesados
    
    # Crear un pool de procesos para el procesamiento concurrente
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        # Enviar tareas de procesamiento de archivos al pool
        future_to_path = {executor.submit(extraer_texto_y_guardar, os.path.join(root, archivo)): os.path.join(root, archivo)
            for root, _, files in os.walk(pdf_directory) for archivo in files if archivo.endswith('.pdf')}
        
        # Procesar cada tarea a medida que se complete
        for future in as_completed(future_to_path):
            pdf_path = future_to_path[future]
            try:
                # Obtener el resultado de la tarea
                tiempo_procesamiento = future.result()
                tiempo_total += tiempo_procesamiento  # Sumar el tiempo de procesamiento al total
                numero_total_archivos += 1  # Incrementar el contador de archivos procesados
                print(f"Texto extraído del archivo {pdf_path}")
            except Exception as e:
                print(f"Error al procesar {pdf_path}: {e}")
    
    # Guardar el resumen del procesamiento al final
    guardar_resumen_procesamiento(tiempo_total, numero_total_archivos)
    print(f"Procesamiento completado. Tiempo total: {tiempo_total:.2f} segundos. Archivos procesados: {numero_total_archivos}.")

#if __name__ == "__main__":
    # Crear las tablas en la base de datos
    #crear_tablas()

    # Configura el directorio principal donde se encuentran las carpetas de 2004 y 2005
# pdf_directory = r"C:\\Users\\DEIMYS CAMARGO\\Documents\\TALLER1\\leerpdf"

    # Procesar todos los PDFs en el directorio y sus subcarpetas utilizando 4 cores
    #procesar_pdfs_en_directorio_recursivo(pdf_directory, num_cores=4)

