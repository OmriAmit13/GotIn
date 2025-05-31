from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from technion_scraper import TechnionUniversity
import atexit
import os 
import shutil
import sys
import traceback
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

app = Flask(__name__)
CORS(app)

### general variables ###
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(ChromeDriverManager().install())

### initialize the university classes ###
technion_university = TechnionUniversity(service, chrome_options)
# TODO : add other universities

### Routes for different universities ###

# Route for Technion University analysis
@app.route('/Technion', methods=['POST'])
def technion_handler():
    try:
        request_data = request.get_json()
        logging.info("Received data: %s", request_data)
        
        # Make sure requested_degree is set
        if 'requested_degree' not in request_data and 'subject' in request_data:
            request_data['requested_degree'] = request_data['subject']
            
        result = technion_university.run(request_data)
        return jsonify(result)

    except Exception as e:
        error_traceback = traceback.format_exc()
        logging.error("Error: %s\n%s", str(e), error_traceback)
        return jsonify({'error': str(e)}), 500
    
# TODO : add other universities routes

# Route to serve the client HTML page
@app.route('/')
def serve_client():
    return send_file('submissionForm.html')

@app.route('/submissionForm.css')
def serve_css():
    return send_file('submissionForm.css')
    
@app.route('/results.html')
def serve_results():
    return send_file('results.html')
    
@app.route('/results.css')
def serve_results_css():
    return send_file('results.css')

### delete __pycache__ directory at shutdown ###

# # Function to delete the __pycache__ directory
# def delete_pycache():
#     pycache_path = os.path.join(os.getcwd(), "__pycache__")
#     if os.path.exists(pycache_path):
#         shutil.rmtree(pycache_path)
#         print("__pycache__ directory deleted.")

# # Register the cleanup function to run when the server shuts down
# atexit.register(delete_pycache)

### main function ###
if __name__ == '__main__':
    import sys
    
    # Default port
    port = 3001
    
    # Check if port is provided as command line argument
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    
    app.run(host='0.0.0.0', port=port, debug=True)
