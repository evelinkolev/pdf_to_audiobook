from flask import Flask, request, jsonify, render_template, send_file
import fitz  # PyMuPDF
from gtts import gTTS
from tempfile import NamedTemporaryFile
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/pdf-to-audio', methods=['POST'])
def pdf_to_audio():
    if 'file' not in request.files:
        logging.error('No file part in the request')
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if not file.filename.endswith('.pdf'):
        logging.error('Uploaded file is not a PDF')
        return jsonify({'error': 'Uploaded file is not a PDF'}), 400

    try:
        pdf_bytes = file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype='pdf')
        text = ''

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()

        if not text.strip():
            logging.error('Extracted text is empty')
            return jsonify({'error': 'Extracted text is empty'}), 500

        logging.debug(f'Extracted text length: {len(text)} characters')
    except Exception as e:
        logging.error(f'Error extracting text from PDF: {e}')
        return jsonify({'error': f'Error extracting text from PDF: {e}'}), 500

    try:
        tts = gTTS(text)

        # Create a temporary file to save the audio
        with NamedTemporaryFile(delete=False) as tmp_file:
            tts.save(tmp_file.name)

        # Send the temporary file as a response
        return send_file(tmp_file.name, mimetype='audio/mpeg', as_attachment=True, download_name='output.mp3')

    except Exception as e:
        logging.error(f'Error converting text to speech: {e}')
        return jsonify({'error': f'Error converting text to speech: {e}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
