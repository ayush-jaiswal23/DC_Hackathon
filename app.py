from flask import Flask, request, jsonify, send_file,render_template
from PIL import Image
import numpy as np
import base64
import io
import json
import re
from collections import Counter, defaultdict
from typing import Dict, Any

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("web.html")

class AdvancedASCIICompressor:
    
    def image_to_ascii(self, image_data: bytes) -> str:
        width= 80
        try:
            image = Image.open(io.BytesIO(image_data))
            
            aspect_ratio = image.height / image.width
            height = int(width * aspect_ratio * 0.5)  
            
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            pixels = np.array(image)
            
            chars = ' .:-=+*#%@'
            ascii_art = self._pixels_to_ascii(pixels, chars)
            
            return ascii_art
            
        except Exception as e:
            raise ValueError(f"Image processing error: {str(e)}")
    
    def _pixels_to_ascii(self, pixels: np.ndarray, chars: str) -> str:
        
        max_val = len(chars) - 1
        char_indices = (pixels * max_val / 255).astype(int)
        ascii_lines = []
        for row in char_indices:
            line = ''.join(chars[idx] for idx in row)
            ascii_lines.append(line)
        
        return '\n'.join(ascii_lines)
    
    def compress_ascii(self, ascii_art: str) -> Dict[str, Any]:
        """Apply compression algorithm to ASCII art"""
        original_size = len(ascii_art)
        
        compressed = self._run_length_encode(ascii_art)
        
        compressed_size = len(compressed)
        ratio = original_size / compressed_size if compressed_size > 0 else 1.0
        savings = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0.0
        
        return {
            'compressed_data': compressed,
            'compression_info': {
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
    
# Initialize compressor
compressor = AdvancedASCIICompressor()

@app.route('/convert', methods=['POST'])
def convert_image():
    """Main API endpoint for image to ASCII conversion with compression"""
    try:
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        image_data = image_file.read()
        
        ascii_art = compressor.image_to_ascii(image_data)
        
        compression_result = compressor.compress_ascii(ascii_art)
        
        return jsonify({
            'success': True,
            'original_ascii': ascii_art,
            'compressed_ascii': compression_result['compressed_data'],
            'compression_info': compression_result['compression_info'],
            
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_type>', methods=['POST'])
def download_file(file_type):
    """Download ASCII file (original or compressed)"""
    try:
        data = request.json
        
        if file_type == 'original':
            content = data.get('original_ascii', '')
            filename = 'ascii_art_original.txt'
        elif file_type == 'compressed':
            content = data.get('compressed_ascii', '')
            filename = 'ascii_art_compressed.txt'
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Create file in memory
        file_obj = io.BytesIO()
        file_obj.write(content.encode('utf-8'))
        file_obj.seek(0)
        
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decompress', methods=['POST'])
def decompress_ascii():
    """Decompress ASCII art (for testing/validation)"""
    try:
        data = request.json
        compressed_data = data.get('compressed_data', '')
        algorithm = data.get('algorithm', 'advanced')
        
        
        if algorithm == 'none':
            decompressed = compressed_data
        else:
            decompressed = "Decompression not fully implemented in this demo"
        
        return jsonify({
            'success': True,
            'decompressed_ascii': decompressed
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'ASCII Art Compressor'})

if __name__ == '__main__':
    app.run(debug=True)