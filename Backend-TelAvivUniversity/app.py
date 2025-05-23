from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from TelAvivUniversity import TelAvivUniversity
import argparse

app = Flask(__name__)
CORS(app)

### general variables ###
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service("./chromedriver-win64/chromedriver.exe")

### initialize the university classes ###
tel_aviv_university = TelAvivUniversity(service, chrome_options)

# Route for Tel Aviv University analysis
@app.route('/TelAviv', methods=['POST'])
def tel_aviv_handler():
    try:
        request_data = request.get_json()
        result = tel_aviv_university.run(request_data)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

### main function ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
    #app.run(host='0.0.0.0', port=5000)
