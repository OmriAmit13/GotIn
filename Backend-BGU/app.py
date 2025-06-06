from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from BenGurionUniversity import BenGurionUniversity
import json

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)  # Enable CORS for all routes in the application

### general variables ###
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
    
# Route for Ben Gurion University analysis
@app.route('/BenGurion', methods=['POST'])
def ben_gurion_handler():
    ben_gurion_university = BenGurionUniversity(service, chrome_options)
    try:
        request_data = request.get_json()
        result = ben_gurion_university.run(request_data)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

### main function ###
if __name__ == '__main__':
    try:
        with open('../config.json', 'r') as f:
            config = json.load(f)
            app.run(host='0.0.0.0', port=config['ports']['bgu']) 
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        app.run(host='0.0.0.0', port=3001)
