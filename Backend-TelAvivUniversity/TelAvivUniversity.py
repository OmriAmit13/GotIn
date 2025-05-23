from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import time

class TelAvivUniversity():

    ### Static Variables ###

    subject_url_dict = {
        "מדעי המחשב": "https://go.tau.ac.il/he/exact/ba/computer",
        "הנדסה אזרחית": "https://engineering.tau.ac.il/welcome_undergrad",
        "הנדסה ביורפואית": "https://go.tau.ac.il/he/engineering/ba/biomedical",
        "הנדסת חשמל": "https://go.tau.ac.il/he/engineering/ba/electrical",
        "הנדסת מכונות": "https://go.tau.ac.il/he/engineering/ba/mechanical",
        "הנדסה תעשייה וניהול": "https://go.tau.ac.il/he/engineering/ba/industrial-engineering",
        "הנדסת תוכנה": "https://go.tau.ac.il/he/exact/ba/electrical-engineering-computer-science",
        "חינוך והוראה": "https://go.tau.ac.il/he/education/ba",
        "משפטים": "https://go.tau.ac.il/he/law/ba/law",
        "מנהל עסקים": "https://go.tau.ac.il/he/management/ba/management",
        "סיעוד": "https://go.tau.ac.il/he/med/ba/nursing",
        "פסיכולוגיה": "https://go.tau.ac.il/he/social-sciences/ba/psychology",
        "כלכלה": "https://go.tau.ac.il/he/social-sciences/ba/economics",
        "הנדסה ביוטכנולוגית": "https://go.tau.ac.il/he/life/ba/biotechnology",
        "רפואה": "https://go.tau.ac.il/he/med/ba/med-doc", 
        "עבודה סוציאלית": "https://go.tau.ac.il/he/social-sciences/ba/social-work",
        "הנדסת חומרים": "https://go.tau.ac.il/he/engineering/ba/materials",
        "מדעי המוח וקוגניציה": "https://go.tau.ac.il/he/neuroscience/ba",
        "פיזיקה": "https://go.tau.ac.il/he/exact/ba/physics",
        "מתמטיקה": "https://go.tau.ac.il/he/exact/ba/math",
        "פיזיותרפיה": "https://go.tau.ac.il/he/med/ba/phys", 
        "ריפוי בעיסוק": "https://go.tau.ac.il/he/med/ba/occu"
    }

    subject_alternative_name_dict = {
        "הנדסת תוכנה": "הנדסת מחשבים",
        "חינוך והוראה": "חינוך",
        "מנהל עסקים": "ניהול",
        "הנדסה ביוטכנולוגית": "ביולוגיה וביוטגנולוגיה"
    }

    subject_sectional_dict = {
        "מדעי המחשב": "מדעים מדויקים",
        "הנדסה אזרחית": "הנדסה",
        "הנדסה ביורפואית": "הנדסה",
        "הנדסת חשמל": "הנדסה",
        "הנדסת מכונות": "הנדסה",
        "הנדסה תעשייה וניהול": "הנדסה",
        "הנדסת תוכנה": "הנדסה",
        "חינוך והוראה": "כללי",
        "משפטים": "כללי",
        "מנהל עסקים": "ניהול",
        "סיעוד": "כללי",
        "פסיכולוגיה": "כללי",
        "כלכלה": "כללי",
        "הנדסה ביוטכנולוגית": "כללי",
        "רפואה": "null", 
        "עבודה סוציאלית": "כללי", 
        "הנדסת חומרים": "הנדסה",
        "מדעי המוח וקוגניציה": "כללי", 
        "פיזיקה": "מדעים מדויקים", 
        "מתמטיקה": "מדעים מדויקים", 
        "פיזיותרפיה": "null", 
        "ריפוי בעיסוק": "כללי" 
    }

    highschool_subject_name_dict = {
        "עברית: הבנה, הבעה ולשון": "הבעה עברית",
        "היסטוריה": "היסטוריה/תע\"י",
        "תושב\"ע": "תורה שבע\"פ",
        "אמנות חזותית": "אמנות",
        "מערכות חשמל": "חשמל",
        "מערכות בקרה": "מכשור ובקרה"
    }

    # this set holds the high school subject that exist explicitly in the form
    highschool_subject_in_form = {
        "אזרחות",
        "אנגלית",
        "מתמטיקה",
        "היסטוריה/תע\"י",
        "הבעה עברית",
        "ספרות",
        "תנ\"ך",
        "ערבית",
        "עברית",
        "אלקטרוניקה",
        "אמנות",
        "ביולוגיה",
        "גיאוגרפיה",
        "חקלאות",
        "חשמל",
        "כימיה",
        "מדעי החברה",
        "מדעי המחשב",
        "מוסיקה",
        "מחשבת ישראל",
        "מכשור ובקרה",
        "מכניקה הנדסית",
        "פיזיקה",
        "פסיכולוגיה",
        "צרפתית",
        "תורה שבע\"פ",
        "תלמוד"
    }

    ### methods ###

    def __init__(self, options):
        self.service = Service(ChromeDriverManager().install())
        self.options = options

    # This method will be executed when the thread starts
    def run(self, data):

        # get relevant url for the subject
        url = self.subject_url_dict[data["subject"]]

        # message to be returned
        msg = ""

        # handle edge case where the required subject is medicine or physiotherapy
        if data["subject"] == "רפואה" or data["subject"] == "פיזיותרפיה":
            result = self.calculate_medicine_threshold(data)
            msg = "עבור רפואה ופיזיותרפיה קבלה משמעותה מעבר תנאי סף על מנת להתחיל בתהליך המיונים ולא בקבלה ללימודים"
        

        # handle case where subject doesn't exist in TLV
        elif data["subject"] == "הנדסה אזרחית":
            result = None
            msg = "הנדסה אזרחית לא קיימת במערכת הקבלה של אוניברסיטת תל אביב. יש לבדוק את המידע באתר האוניברסיטה."

        # handle general case
        else:
            if data["subject"] in self.subject_alternative_name_dict.keys():
                data["subject"] = self.subject_alternative_name_dict[data["subject"]]
            match_scores = self.get_tlv_match_scores(data)
            result = self.is_accepted_per_subject(data, match_scores)
        
        return {"isAccepted": result, "url": url, "message": msg}

    # This function scrapes the TLV high school score from the website
    def get_tlv_highschool_score(self, highschool_scores):

        # create a copy of the dictionary to avoid modifying the original
        scores = highschool_scores.copy()

        # Replace subject names with university's naming
        for subject in scores.copy():
            if subject in self.highschool_subject_name_dict:
                scores[self.highschool_subject_name_dict[subject]] = scores.pop(subject)
        
        # Replace subject names that don't appear in the form explicitly with "אחר ללא בונוס"
        special_subjects = []
        for subject in scores.copy():
            if subject not in self.highschool_subject_in_form:
                special_subjects.append(scores.pop(subject))

        # Provide the correct path to your ChromeDriver executable
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.get("https://www.ims.tau.ac.il/md/calc/Bagrut.aspx")

        # extract the form element
        form = driver.find_element(By.TAG_NAME, "form")

        # extract the subject lines from the form
        free_tables = form.find_element(By.CLASS_NAME, "trtblscont")
        lines = free_tables.find_elements(By.TAG_NAME, "tr")

        # iterate over the lines and fill in the scores
        for line in lines:

            # check if the line contains input elements
            if (line.find_elements(By.TAG_NAME, "input")):

                # get the subject name from the line
                tds = line.find_elements(By.TAG_NAME, "td")
                subject_name = tds[2].text

                # make sure the subject name matches that in the scores dictionary
                for name in scores.keys():
                    if name in subject_name:
                        subject_name = name
                        break
                
                # handle case where subject isn't in the dictionary
                if subject_name not in scores.keys() and subject_name != "אחר ללא בונוס":
                    continue
                
                # handle case where we're at special subject line but there are no special subjects left
                if subject_name == "אחר ללא בונוס" and len(special_subjects) <= 0:
                    continue

                # get the subject data from the appropriate source
                if subject_name == "אחר ללא בונוס":
                    subject_data = special_subjects.pop(0)
                else:
                    subject_data = scores.pop(subject_name)
                
                # get the grade and units for the subject
                grade = subject_data[0]
                units = subject_data[1]

                # Enter grade and units for the subject
                input_grade = tds[0].find_element(By.TAG_NAME, "input")
                input_units = tds[1].find_element(By.TAG_NAME, "input")
                input_grade.send_keys(grade)
                input_units.send_keys(units)

        # Find and click the submit button safely
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
        )

        # Scroll into view and click
        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        driver.execute_script("arguments[0].click();", submit_button)

        # Wait for the results page to load
        WebDriverWait(driver, 10).until(EC.url_contains("Bagrut_T.aspx"))

        # Extract results
        result_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        result_line = result_element.find_element(By.CLASS_NAME, "rowalter")
        output = result_line.find_elements(By.TAG_NAME, "td")[2].text

        driver.quit()

        return output.replace(" ", "")

    # This function scrapes the TLV match score from the website
    def get_tlv_match_scores(self, inputJson):

        # extract scores from inputJson
        psycho_score = inputJson["psycho_score"]
        hs_dict = inputJson["highschool_scores"]
        highschool_score = self.get_tlv_highschool_score(hs_dict)
        
        # Provide the correct path to your ChromeDriver executable
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.get("https://go.tau.ac.il/he/calculator")
        
        # extract the input elements from the form
        form = driver.find_element(By.TAG_NAME, "form")
        [highschool_input, psycho_input, units_5_button] = form.find_elements(By.TAG_NAME, "input")
        
        # enter inputs into the form
        highschool_input.send_keys(highschool_score)
        psycho_input.send_keys(psycho_score)
        if (hs_dict["מתמטיקה"][1] == "5" and "פיזיקה" in hs_dict.keys() and hs_dict["פיזיקה"][1] == "5"):
            units_5_button.click()

        # Find and click the submit button
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.calc-btn.btn.btn-dark"))
        )

        # Scroll into view and click
        driver.execute_script("arguments[0].scrollIntoView();", submit_button)
        driver.execute_script("arguments[0].click();", submit_button)

        continue_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.suitability-calc.faculty-filter-shown.container-fluid"))
        )

        # get general score
        general_result = continue_element.find_element(By.CLASS_NAME, "result-score").text

        # get sectional scores
        sectional_results = continue_element.find_element(By.TAG_NAME, "table").find_element(By.CLASS_NAME, "tr-r").find_elements(By.TAG_NAME, "td")
        [engineering_score, exact_score, nomor_score, management_score] = [sectional_results[i].text for i in range(len(sectional_results))]
        
        driver.quit()

        return {
            "הנדסה": engineering_score,
            "מדעים מדויקים": exact_score,
            "ללא מור": nomor_score,
            "ניהול": management_score,
            "כללי": general_result
        }

    # This function scrapes the TLV match score from the website
    def is_accepted_per_subject(self, inputJson, match_scores):

        # find which url to go to according to the subject
        url = self.subject_url_dict[inputJson["subject"]]

        # Provide the correct path to your ChromeDriver executable
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.get(url)

        # Wait for the popup close button to appear and click it
        try:
            close_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ui-dialog-titlebar-close"))
            )
            close_button.click()
        except:
            pass

        main_content = driver.find_element(By.ID, "main-content")
        required_scores = main_content.find_element(By.ID, "acceptancechances").find_element(By.CLASS_NAME, "right-half").find_element(By.CLASS_NAME, "indexing")

        # get the acceptance and rejection thresholds and my score
        acceptance_threshold = int(required_scores.find_element(By.ID, "acceptanceThreshold").get_attribute("innerHTML"))
        rejection_threshold = int(required_scores.find_element(By.ID, "rejectionThreshold").get_attribute("innerHTML"))
        my_score = int(match_scores[self.subject_sectional_dict[inputJson["subject"]]])

        driver.quit()

        if (my_score >= acceptance_threshold):
            return "קבלה"
        elif (my_score >= rejection_threshold):
            return "רשימת המתנה"
        else:
            return "דחייה"
        
    # Thisd function handles medcine and physiotherapy acceptance since you can't get the result from the website
    def calculate_medicine_threshold(self, inputJson):
        
        # get the necessary threshold for the psychometric score according to which subject the user is applying for
        subject = inputJson["subject"]
        if subject == "רפואה":
            psycho_score_threshold = 700
        else:
            psycho_score_threshold = 630
        
        # calculate whether the user is accepted or rejected according to the psychometric score and the high school scores
        if int(inputJson["psycho_score"]) >= psycho_score_threshold and int(inputJson["highschool_scores"]["מתמטיקה"][0]) >= 56 and int(inputJson["highschool_scores"]["מתמטיקה"][1]) >= 4 and int(inputJson["psycho_english"]) >= 120:
            return "קבלה"
        else:
            return "דחייה"


if __name__ == '__main__':
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    uni = TelAvivUniversity(options)

    # Load the input JSON file
    with open("input.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    start_time = time.time()
    print(uni.run(data))
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")
