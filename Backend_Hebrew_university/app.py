from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from HebrewUniversity import HebrewUniversity
import atexit
import os
import shutil
import json
import traceback
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)

### general variables ###
chrome_options = Options()
chrome_options.add_argument("--headless")

#service = Service(r"C:\Users\Raz Zana\Desktop\chromedriver-win64\chromedriver.exe")
service = Service(ChromeDriverManager().install())


### initialize the university classes ###
hebrew_university = HebrewUniversity(service, chrome_options)


# Route for hebrew University analysis
@app.route('/HebrewUniversity', methods=['POST'])
def hebrew_handler():
    try:
        request_data = request.get_json()

        print("📦 Received JSON:", request_data)
        print(json.dumps(request_data, indent=2, ensure_ascii=False))  # תומך בעברית
        

        result = hebrew_university.run(request_data)
        return jsonify(result)

    except Exception as e:
        print("❌ Error during request:")
        traceback.print_exc()  # מדפיס את השגיאה המלאה לטרמינל!
        return jsonify({'error': str(e)}), 500
    

### main function ###
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002)