import os
import pytesseract
from pdf2image import convert_from_path
from concurrent.futures import ProcessPoolExecutor, as_completed
import datetime
import sqlite3

# Configurar la ruta al ejecutable de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Función para crear la tabla si no existe
def crear_tabla():
    db_path = 'procesamiento_pdfs.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS procesamiento_pdf (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_procesamiento TEXT,
            ruta_archivo TEXT,
            nombre_archivo TEXT,
            tiempo_procesamiento REAL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"La base de datos se está guardando en: {os.path.abspath(db_path)}")

# Función para extraer texto de un PDF y almacenarlo en la base de datos
def extraer_texto_y_guardar(pdf_path, ocr_language='spa'):
    start_time = datetime.datetime.now()
    imagenes = convert_from_path(pdf_path)
    texto_total = ""
    for num_pagina, imagen in enumerate(imagenes):
        texto_extraido = pytesseract.image_to_string(imagen, lang=ocr_language)
        texto_total += f"\n--- Página {num_pagina + 1} ---\n"
        texto_total += texto_extraido
    end_time = datetime.datetime.now()
    tiempo_procesamiento = (end_time - start_time).total_seconds()
    
    # Guardar en la base de datos
    guardar_en_base_de_datos(pdf_path, tiempo_procesamiento)
    
    return texto_total, tiempo_procesamiento

# Función para guardar en la base de datos SQLite
def guardar_en_base_de_datos(pdf_path, tiempo_procesamiento):
    conn = sqlite3.connect('procesamiento_pdfs.db')
    cursor = conn.cursor()
    nombre_archivo = os.path.basename(pdf_path)
    fecha_procesamiento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO procesamiento_pdf (fecha_procesamiento, ruta_archivo, nombre_archivo, tiempo_procesamiento) VALUES (?, ?, ?, ?)',
            (fecha_procesamiento, pdf_path, nombre_archivo, tiempo_procesamiento))
    conn.commit()
    conn.close()

# Función para procesar PDFs en un directorio recursivamente
def procesar_pdfs_en_directorio_recursivo(pdf_directory, num_cores=4):
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        future_to_path = {executor.submit(extraer_texto_y_guardar, os.path.join(root, archivo)): os.path.join(root, archivo)
            for root, _, files in os.walk(pdf_directory) for archivo in files if archivo.endswith('.pdf')}
        
        for future in as_completed(future_to_path):
            pdf_path = future_to_path[future]
            try:
                texto_extraido, tiempo_procesamiento = future.result()
                output_txt_path = pdf_path.replace('.pdf', '.txt')
                with open(output_txt_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(texto_extraido)
                print(f"Texto extraído y guardado en {output_txt_path}")
            except Exception as e:
                print(f"Error al procesar {pdf_path}: {e}")

if __name__ == "__main__":
    # Crear la tabla en la base de datos
    crear_tabla()

    # Configura el directorio principal donde se encuentran las carpetas de 2004 y 2005
    pdf_directory = r"C:\\Users\\DEIMYS CAMARGO\\Documents\\TALLER1\\leerpdf"

    # Procesar todos los PDFs en el directorio y sus subcarpetas utilizando 4 cores
    procesar_pdfs_en_directorio_recursivo(pdf_directory, num_cores=4)
