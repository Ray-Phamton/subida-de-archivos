from tokenize import Ignore
from flask import Flask, render_template, request, send_from_directory, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS

app = Flask(__name__)
CARGAR_ARCHIVO = 'static/uploads'
app.config['CARGAR_ARCHIVO'] = CARGAR_ARCHIVO
EXTENSIONES_PERMITIDAS = {'txt','html', 'py', 'css', 'jpg', 'jpeg', 'png'}

if not os.path.exists(CARGAR_ARCHIVO):
    os.makedirs(CARGAR_ARCHIVO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in EXTENSIONES_PERMITIDAS    

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    image_url = None
    error = None

    if request.method == 'POST':

        if 'file' not in request.files:
            error = 'No se seleccionó ningún archivo.'
            return render_template('index.html', error=error)

        file = request.files['file']

        if file.filename == '':
            error = 'Nombre de archivo vacío'
            return render_template('index.html', error=error)

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['CARGAR_ARCHIVO'],filename)
               
            try:
                file.save(filepath)
                
            except Exception as e:
                error = f"No se pudo guardar el archivo: {str(e)}"
                return render_template('index.html', error=error)

            ext = filename.rsplit('.', 1)[1].lower()

            if ext in {'txt', 'html', 'py', 'css'}:
                result = analyze_text_file(filepath)
            elif ext in {'jpg', 'jpeg', 'png'}:
                result = extract_image_metadata(filepath)
                image_url = url_for('static', filename=f'uploads/{filename}')
            else:
                error = 'Tipo de archivo no soportado'
        else:
            error = 'Archivo no permitido'

    return render_template('index.html', result = result , image_url = image_url, error = error)

def analyze_text_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors = Ignore) as f:
            contenido = str(f.read())
            lineas = contenido.splitlines()
            palabras = contenido.split()
            caracter = len(contenido) 

            vista = "\n"+contenido

        return {
            'tipo': 'texto',
            'lineas': len(lineas),
            'palabras': len(palabras),
            'caracteres': caracter,
            'vista': vista
        }
    except Exception as e:
        return {'error': str(e)}

def extract_image_metadata(filepath):
    try:
        image = Image.open(filepath)
        info = image._getexif()
        metadata = {'tipo':'imagen'}

        etiquetas_deseadas = {
            'ImageWidth', 'ImageLength', 'GPSInfo', 'Make',
            'Model', 'Software', 'DateTime'
        }

        if info:
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name in etiquetas_deseadas:
                    metadata[tag_name] = str(value)
        else:
            metadata['Info'] = 'Sin metadatos disponibles'

        return metadata
    except Exception as e:
        return {'error': str(e)}


def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__== '__main__':
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, port=5000)

