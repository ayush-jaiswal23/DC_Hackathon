from flask import Flask, request, jsonify, send_file,render_template
from flask_cors import CORS
from PIL import Image
import numpy as np
import base64
import io
import re
from typing import Dict, Any
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])  
@app.route("/")
def index():
    try:
        return render_template("web.html")
    except FileNotFoundError:
        return "index.html not found. Make sure it's in the same directory as this script."

class AdvancedASCIICompressor:
    
    def image_to_ascii(self, image_data: bytes, width: int = 80) -> str:
        try:
            logger.info(f"Processing image, size: {len(image_data)} bytes")
            
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Original image size: {image.size}, mode: {image.mode}")
            
            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')
                logger.info("Converted to grayscale")
            
            aspect_ratio = image.height / image.width
            height = int(width * aspect_ratio * 0.5)  
            logger.info(f"Resizing to: {width}x{height}")
            
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            pixels = np.array(image)
            logger.info(f"Pixel array shape: {pixels.shape}")
            
            chars = ' .:-=+*#%@'
            ascii_art = self._pixels_to_ascii(pixels, chars)
            
            logger.info(f"Generated ASCII art, length: {len(ascii_art)}")
            logger.info(f"First 100 chars: {ascii_art[:100]}")
            
            return ascii_art
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Image processing error: {str(e)}")
    
    def _pixels_to_ascii(self, pixels: np.ndarray, chars: str) -> str:
        max_val = len(chars) - 1
        char_indices = (pixels * max_val / 255).astype(int)
        ascii_lines = []
        for row in char_indices:
            line = ''.join(chars[idx] for idx in row)
            ascii_lines.append(line)
        
        return '\n'.join(ascii_lines)
    
    def compress_ascii(self, ascii_art: str, algorithm: str = 'advanced') -> Dict[str, Any]:
        original_size = len(ascii_art)
        logger.info(f"Compressing ASCII art, original size: {original_size}")
        
        if algorithm == 'advanced':
            compressed = self._run_length_encode(ascii_art)
        else:
            compressed = ascii_art  # No compression
        
        compressed_size = len(compressed)
        ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        savings = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0.0
        
        logger.info(f"Compression complete - ratio: {ratio:.2f}, savings: {savings:.1f}%")
        
        return {
            'compressed_data': compressed,
            'compression_info': {
                'algorithm': algorithm,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'ratio': round(ratio, 2),
                'savings_percent': round(savings, 1)
            }
        }
    
    def _run_length_encode(self, data: str) -> str:
        if not data:
            return ""
        
        encoded = []
        i = 0
        
        while i < len(data):
            current_char = data[i]
            count = 1
            
            while i + count < len(data) and data[i + count] == current_char and count < 9999:
                count += 1
            
            if count >= 4 or (current_char in ' \n' and count >= 2):
                encoded.append(f"#{count}{current_char}")
            elif count >= 2 and current_char not in ' \n':
                encoded.append(f"${count}{current_char}")
            else:
                encoded.append(current_char * count)
            
            i += count
        
        return ''.join(encoded)

compressor = AdvancedASCIICompressor()

@app.route('/convert', methods=['POST', 'OPTIONS'])
def convert_image():
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        logger.info("Handling CORS preflight request")
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    try:
        logger.info("=== NEW CONVERSION REQUEST ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Request files: {list(request.files.keys())}")
        logger.info(f"Request form: {dict(request.form)}")
        
        if 'file' not in request.files:
            logger.error("No 'file' in request.files")
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
            
        image_file = request.files['file']
        logger.info(f"Received file: {image_file.filename}")
        
        if image_file.filename == '':
            logger.error("Empty filename")
            return jsonify({'success': False, 'error': 'No image file selected'}), 400
        
        image_data = image_file.read()
        logger.info(f"Read {len(image_data)} bytes from file")
        
        if len(image_data) == 0:
            logger.error("Empty image data")
            return jsonify({'success': False, 'error': 'Empty image file'}), 400
        
        # Get optional parameters with defaults
        width = int(request.form.get('width', 80))
        char_set = request.form.get('char_set', 'standard')
        compression = request.form.get('compression', 'advanced')
        
        logger.info(f"Parameters - width: {width}, char_set: {char_set}, compression: {compression}")
        
        ascii_art = compressor.image_to_ascii(image_data, width)
        
        if not ascii_art:
            logger.error("ASCII art generation returned empty result")
            return jsonify({'success': False, 'error': 'Failed to generate ASCII art'}), 500
        
        compression_result = compressor.compress_ascii(ascii_art, compression)
        
        response_data = {
            'success': True,
            'original_ascii': ascii_art,
            'compressed_ascii': compression_result['compressed_data'],
            'compression_info': compression_result['compression_info']
        }
        
        logger.info("Conversion completed successfully!")
        logger.info(f"Response data keys: {list(response_data.keys())}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    return jsonify({'status': 'healthy', 'service': 'ASCII Art Compressor'})

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify server is working"""
    logger.info("Test endpoint accessed")
    return jsonify({'message': 'Server is working!', 'timestamp': str(app.logger)})
if __name__ == '__main__':
    app.run(debug=True)