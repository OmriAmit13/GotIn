from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
# Commented out TelAvivUniversity import since it's not available yet
# from TelAvivUniversity import TelAvivUniversity
from BenGurionUniversity import BenGurionUniversity
import atexit
import os
import shutil

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)  # Enable CORS for all routes in the application

# Route for static files
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def send_file(path):
    return send_from_directory(app.static_folder, path)

### general variables ###
chrome_options = Options()
#chrome_options.add_argument("--headless")
service = Service(ChromeDriverManager().install())

### initialize the university classes ###
# Commented out TelAvivUniversity initialization since it's not available yet
# tel_aviv_university = TelAvivUniversity(service, chrome_options)
ben_gurion_university = BenGurionUniversity(service, chrome_options)

### Routes for different universities ###

# Route for Tel Aviv University analysis - Commented out since TelAvivUniversity is not available yet
# @app.route('/TelAviv', methods=['POST'])
# def tel_aviv_handler():
#     try:
#         request_data = request.get_json()
#         result = tel_aviv_university.run(request_data)
#         return jsonify(result)
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
# Route for Ben Gurion University analysis
@app.route('/BenGurion', methods=['POST'])
def ben_gurion_handler():
    try:
        request_data = request.get_json()
        result = ben_gurion_university.run(request_data)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    # Using port 5001 to match frontend expectations
    app.run(host='0.0.0.0', port=3004)
