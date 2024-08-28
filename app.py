from flask_cors import CORS
from flask import Flask, request, jsonify
from main import procesar_pdfs_en_directorio_recursivo
from main import crear_tablas

app = Flask(__name__)

CORS(app) #seguridad de la api
pdf_directory = r"C:\\Users\\DEIMYS CAMARGO\\Documents\\TALLER1\\leerpdf"

@app.route('/procesarcores', methods=['POST'])
def recibir_datos():
    # Obtener los datos enviados en la solicitud

    numCores = int(request.form.get('numCores'))
    #print(numCores)
    try:

        procesar_pdfs_en_directorio_recursivo(pdf_directory, numCores)
        # Devolver la respuesta como JSON
        return jsonify(
            {
            "numCores" : numCores,
            "mensaje" : "El número de cores que has configurado es: "
            }
        ), 201
    except Exception as e:
        print(e)
        return jsonify("Ha sucedido un error"), 500
    

if __name__ == '__main__':
    crear_tablas()
    
    app.run(debug=True)