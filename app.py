import os
import subprocess
import uuid
import shutil
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/split": {"origins": "*"}})

# This is a temporary directory for file uploads. In a production environment,
# you might want to use a more robust storage solution.
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/split', methods=['POST'])
def split_pdf():
    """
    Splits a PDF based on page ranges.
    Expects a POST request with a 'file' (the PDF) and 'ranges' (a comma-separated string of page ranges).
    Example ranges: '1-3,5,7-10'
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file type, please upload a PDF"}), 400

    ranges_str = request.form.get('ranges')
    if not ranges_str:
        return jsonify({"error": "No page ranges provided"}), 400

    # Create a unique temporary directory for this request to handle concurrent requests safely
    request_id = str(uuid.uuid4())
    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], request_id)
    os.makedirs(temp_dir)

    try:
        input_pdf_path = os.path.join(temp_dir, file.filename)
        file.save(input_pdf_path)

        ranges = [r.strip() for r in ranges_str.split(',')]
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(output_dir)
        output_filenames = []

        for page_range in ranges:
            sanitized_range = page_range.replace('-', '_').replace(' ', '')
            output_filename = f"pages_{sanitized_range}.pdf"
            output_pdf_path = os.path.join(output_dir, output_filename)

            command = [
                'qpdf',
                input_pdf_path,
                '--pages',
                '.',  # Use the main input file specified before --pages
                page_range,
                '--',
                output_pdf_path
            ]

            result = subprocess.run(command, capture_output=True, text=True, check=False)

            # Log any non-zero exit code for diagnostics but only treat it as fatal
            # if qpdf didn’t produce the requested output file.
            if result.returncode != 0:
                app.logger.warning(
                    f"qpdf exit {result.returncode} for range '{page_range}': {result.stderr.strip()}"
                )

            if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                output_filenames.append(output_filename)
            else:
                raise ValueError(
                    f"Failed to process range '{page_range}': no output produced by qpdf"
                )

        if not output_filenames:
            return jsonify({"error": "No pages were extracted. Please check your page ranges."}), 400

        # If only one file was created, send it directly
        if len(output_filenames) == 1:
            single_file_path = os.path.join(output_dir, output_filenames[0])
            return send_file(single_file_path, as_attachment=True, download_name=output_filenames[0])

        # If multiple files were created, zip them up
        zip_base_path = os.path.join(temp_dir, 'split_files')
        zip_path = shutil.make_archive(zip_base_path, 'zip', output_dir)

        return send_file(zip_path, as_attachment=True, download_name='split_files.zip')

    except (ValueError, FileNotFoundError) as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred.", "details": str(e)}), 500
    finally:
        # Clean up the temporary directory and its contents
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    # Local development entry point (not used in production Docker build)
    app.run(host='0.0.0.0', port=5001)
