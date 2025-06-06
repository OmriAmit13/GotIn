from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from technion_scraper import TechnionUniversity
import sys
import traceback
import logging
import json

app = Flask(__name__)
CORS(app)

### general variables ###
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--autoplay-policy=user-gesture-required")
chrome_options.add_argument("--mute-audio")
chrome_options.add_experimental_option("prefs", {
    "media.autoplay.enabled": False,
    "media.autoplay.allow-extension-media": False,
})
service = Service(ChromeDriverManager().install())

# Route for Technion University analysis
@app.route('/Technion', methods=['POST'])
def technion_handler():
    ### initialize the university classes ###
    technion_university = TechnionUniversity(service, chrome_options)
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

### main function ###
if __name__ == '__main__':
    try:
        with open('../config.json', 'r') as f:
            config = json.load(f)
            app.run(host='0.0.0.0', port=config['ports']['technion']) 
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        app.run(host='0.0.0.0', port=3003)
