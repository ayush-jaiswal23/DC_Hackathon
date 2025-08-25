from flask import Flask, render_template, redirect,request,url_for
from PIL import Image
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

def imageToAscii(image):

    # Mapping symbols for compression
    cmp = {
        "!": "@@",   
        "#": "**",   
        "$": "``",   
        "%": "@\n",  
        "^": "*\n",  
        "&": "`\n"   
    }
    
    width, height = image.size
    output_string = ""

    # Original ASCII symbols
    symbols = {
        'black': '@',
        'white': '-',
        'grey':  '*'
    }

    for y in range(height):
        for x in range(width):
            pixel_value = image.getpixel((x, y))
            if pixel_value <= 85:
                output_string += symbols['black']
            elif pixel_value <= 170:
                output_string += symbols['grey']
            else:
                output_string += symbols['white']
        output_string += '\n'

    size_in_bytes = len(output_string.encode('utf-8'))
    size_in_kb = size_in_bytes / 1024


    # Store converted file size
    print("Converted file size:", size_in_kb, " kb")

    compressed_text = output_string
    for key, value in cmp.items():
        compressed_text = compressed_text.replace(value, key)

    decompressed_text = compressed_text
    for key, value in cmp.items():
        decompressed_text = decompressed_text.replace(key, value)

    return decompressed_text
    

@app.route('/display',methods=['POST'])
def display():
    image_file = request.files["image"]
    if not image_file:
        return redirect(url_for('/'))
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
    image_file.save(filepath)
    file_url = url_for('static', filename=f'uploads/{image_file.filename}')
    imageBinary = Image.open(image_file).convert('L')
    
    asciiArt = imageToAscii(image = imageBinary)

    return render_template('imagedisplay.html',asciiArt= asciiArt,actualImage=file_url)
