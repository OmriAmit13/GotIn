from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from TelAvivUniversity import TelAvivUniversity
import argparse
import json

app = Flask(__name__)
CORS(app)

### general variables ###
chrome_options = Options()
chrome_options.add_argument("--headless")

# Route for Tel Aviv University analysis
@app.route('/TelAviv', methods=['POST'])
def tel_aviv_handler():
    tel_aviv_university = TelAvivUniversity(chrome_options)
    try:
        request_data = request.get_json()
        result = tel_aviv_university.run(request_data)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

### main function ###
if __name__ == '__main__':
    try:
        with open('../config.json', 'r') as f:
            config = json.load(f)
            app.run(host='0.0.0.0', port=config['ports']['tel_aviv']) 
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        app.run(host='0.0.0.0', port=3004)
