import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait, Select

class HebrewUniversity:

    # === Static Variables ===
    CORE_SUBJECTS = [
        "אזרחות",
        "עברית: הבנה, הבעה ולשון",
        "אנגלית",
        "מתמטיקה",
        "פיזיקה",
        "ספרות",
        "היסטוריה",
        "תנ\"ך"
    ]
    DEGREES_DATA = [
        {
            "user_input": "מדעי המחשב",
            "site_option_1": "מדעי המחשב",
            "site_option_2": "מדעי המחשב, חד-חוגי"
        },
        {
            "user_input": "חינוך והוראה",
            "site_option_1": "חינוך",
            "site_option_2": "חינוך, דו-חוגי"
        },
        {
            "user_input": "מנהל עסקים",
            "site_option_1": "מנהל עסקים",
            "site_option_2": "מנהל עסקים,דו-חוגי"
        },
        {
            "user_input": "סיעוד",
            "site_option_1": "אחיות (סיעוד)",
            "site_option_2": "אחיות (סיעוד), חד-חוגי, בי\"ח הדסה"
        },
        {
            "user_input": "הנדסת חשמל",
            "site_option_1": "הנדסת חשמל ומדעי המחשב או",
            "site_option_2": "הנדסת חשמל ופיסיקה יישומית, חד-חוגי"
        },
        {
            "user_input": "משפטים",
            "site_option_1": "משפטים",
            "site_option_2": "משפטים, חד-חוגי"
        },
        {
            "user_input": "פסיכולוגיה",
            "site_option_1": "פסיכולוגיה",
            "site_option_2": "פסיכולוגה, דו-חוגי"
        },
        {
            "user_input": "כלכלה",
            "site_option_1": "כלכלה",
            "site_option_2": "כלכלה, דו-חוגי"
        },
        {
            "user_input": "רפואה",
            "site_option_1": "רפואה",
            "site_option_2": "רפואה,חד-חוגי, לימודים פרה קליניים"
        },
        {
            "user_input": "עבודה סוציאלית",
            "site_option_1": "עבודה סוציאלית",
            "site_option_2": "עבודה סוציאלית, חד חוגי"
        },
        {
            "user_input": "מתמטיקה",
            "site_option_1": "מתמטי'ה",
            "site_option_2": "מתמטיקה, חד חוגי"
        },
        {
            "user_input": "פיזיקה",
            "site_option_1": "פיסיקה",
            "site_option_2": "פיסיקה, חד-חוגי"
        },
        {
            "user_input": "מדעי המוח וקוגניציה" ,
            "site_option_1": "מדעי המוח",
            "site_option_2": "מדעי הקוגניציה והמוח, דו-חוגי"
        },
        {
            "user_input": "ריפוי בעיסוק",
            "site_option_1": "ריפוי בעיסוק",
            "site_option_2": "ריפוי בעיסוק, חג-חוגי"
        }
    ]

    SUBJECT_NAME_MAP = {
            "תנ\"ך":"תנ\"ך",
            "תנך": "תנ\"ך",
            "עברית": "עברית: הבנה, הבעה ולשון",
            "ספרות": "ספרות",
            "אנגלית": "אנגלית",
            "היסטוריה": "היסטוריה",
            "אזרחות": "אזרחות",
            "מתמטיקה": "מתמטיקה",
            "פיזיקה": "פיזיקה"
        }

    
    def __init__(self, service, options):
            self.service = service
            self.options = options
            
    def take_screenshot(self, driver, prefix="debug"):
        """Take a full page screenshot with the given driver and return the path"""
        if not driver:
            print("Cannot take screenshot - no driver provided")
            return None
            
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_path = f"{prefix}_screenshot_{timestamp}.png"
        try:
            # Get original window size
            original_size = driver.get_window_size()
            
            # Get the entire page height
            total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
            total_width = driver.execute_script("return document.body.parentNode.scrollWidth")
            
            # Set window size to capture everything
            driver.set_window_size(total_width, total_height)
            
            # Take screenshot
            driver.save_screenshot(screenshot_path)
            print(f"📸 Full page screenshot saved to: {screenshot_path}")
            
            # Restore original window size
            driver.set_window_size(original_size['width'], original_size['height'])
            
            return screenshot_path
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None


    def get_site_degree_options(self,user_input):

        for item in self.DEGREES_DATA:
            if item["user_input"] == user_input:
                return item["site_option_1"], item["site_option_2"]
        return user_input, user_input  # fallback if not found



    def calculate_psychometric_emphases(self,total,verbal, quantitative, english):
        emphases = {
            "verbal_emphasis": {
                "name": "דגש מילולי",
                "weights": {"verbal": 0.6, "quant": 0.2, "english": 0.2}
            },
            "quant_emphasis": {
                "name": "דגש כמותי",
                "weights": {"verbal": 0.2, "quant": 0.6, "english": 0.2}
            },
            "multi_emphasis": {
                "name": "דגש רב תחומי",
                "weights": {"verbal": 0.4, "quant": 0.4, "english": 0.2}
            }
        }

        results = {}

        for key, data in emphases.items():
            w = data["weights"]
            score = round(
                verbal * w["verbal"] +
                quantitative * w["quant"] +
                english * w["english"]
            )
            original_avg = (verbal + quantitative + english) / 3
            delta = score - original_avg

            # מקדם תיקון משוער – מעלה או מוריד מהציון הכללי לפי ההטיה
            correction_factor = 5.33
            emphasis_score = round(total + delta * correction_factor)

            # הגבלה בין 200 ל־800
            emphasis_score = max(200, min(800, emphasis_score))
            results[key] = emphasis_score 

        return results


    def fill_psychometric_fields(self, fields, psycho_scores):
        try:
        # unpack 3 scores
            total, quant_score, verbal_score, english_score = psycho_scores

            # מחשבים את הדגשים
            emphases = self.calculate_psychometric_emphases(total,verbal_score, quant_score, english_score)

            # שמים את הדגשים בסדר: כמותי, מילולי, רב תחומי
            emphasis_values = [
                emphases["quant_emphasis"],
                emphases["verbal_emphasis"],
                emphases["multi_emphasis"]
            ]

            for i, field in enumerate(fields):
                if i >= len(emphasis_values):
                    print(f"Field #{i+1} skipped — no matching emphasis value")
                    break

                value = str(int(emphasis_values[i]))

                # Use JavaScript to set the value instead of direct input
                input_el = field.find_element(By.TAG_NAME, "input")
                
                # Scroll the element into view first
                driver = input_el.parent
                driver.execute_script("arguments[0].scrollIntoView(true);", input_el)
                time.sleep(0.5)
                
                # Clear and set value using JavaScript
                driver.execute_script("arguments[0].value = '';", input_el)
                driver.execute_script(f"arguments[0].value = '{value}';", input_el)
                
                # Trigger change event to ensure the value is registered
                driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", input_el)
                driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", input_el)
                
                time.sleep(0.5)

                confirmed_value = input_el.get_attribute("value")
                if confirmed_value.strip() != value:
                    print(f"⚠️ Field #{i+1} lost its value, retrying with JavaScript...")
                    driver.execute_script(f"arguments[0].value = '{value}';", input_el)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", input_el)
                    time.sleep(0.5)

                print(f"✅ Filled field #{i+1} with emphasis value: {value}")

            time.sleep(2)

        except Exception as e:
            print(f"❌ Error in fill_psychometric_fields: {e}")


    # === first website ===
    def getDriver1(self):    
        
        # driver = webdriver.Chrome(service=self.service)
        driver = webdriver.Chrome(service=self.service, options=self.options)

        driver.get("https://bagrut-calculator.huji.ac.il/calculator/#/grade-input")

        time.sleep(3)

        return driver


    def firstPageOfCalculator(self, driver):    

        btn_group = driver.find_element(By.CLASS_NAME, "btn-group")

        # Find all buttons inside the group
        buttons = btn_group.find_elements(By.TAG_NAME, "button")

        # Click the SECOND button (index 1)
        if len(buttons) > 1:
            buttons[1].click()
        else:
            print("Second button not found!")

        first_item = driver.find_elements(By.CLASS_NAME, "dropdown-item")[0]
        first_item.click()

        #click the "Next" button
        btn_show = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-show")))

        btn_show.click()

        WebDriverWait(driver, 10).until(EC.url_contains("/grade-input"))

    
    def secondPageOfCalculator(self, driver,scores):

        print("Now on page 2!")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.subject-title span")))
        
        #Find and print subject names
        subject_rows = driver.find_elements(By.CSS_SELECTOR, 'div.input-data')
        
        for i, line in enumerate(subject_rows):
            # Check if the line contains an input element (indicating it's a subject row)  
            if (line.find_elements(By.TAG_NAME, "input")):

                subject_name_el = line.find_element(By.CSS_SELECTOR, 'div.subject-title span')
                subject_name = subject_name_el.text.strip()

                print(f"Subject #{i + 1}: {subject_name}")

                normalized_name = self.SUBJECT_NAME_MAP.get(subject_name, subject_name)

                if normalized_name not in scores:
                    print(f"⚠️ Subject '{subject_name}' (mapped to '{normalized_name}') was not found in the input JSON")
                    continue

                #take from the json   
                # here to change i need to make a map from subjectname to the json 

                grade = scores[normalized_name][0]
                inits= scores[normalized_name][1]

                # Enter units  for the subject

                #click in the dropdown
                dropdown_toggle = line.find_element(By.CSS_SELECTOR, "div.subject-units button.dropdown-toggle-split")
                dropdown_toggle.click()

                #the options in the dropdown
                options = line.find_elements(By.CSS_SELECTOR, "div.subject-units .dropdown-menu a.dropdown-item")
                for option in options:
                    if option.text.strip() == str(inits):
                        option.click()
                        break

                #write the grade
                input_grade = line.find_element(By.CSS_SELECTOR, 'div.subject-grade input')
                input_grade.clear()
                input_grade.send_keys(str(grade))

        #add more subjects
        for subject_name in scores.keys():
            if subject_name not in self.CORE_SUBJECTS:
                print(f"Adding new subject: {subject_name}")

                add_span = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'הוסף מקצוע')]"))
            )
                add_button = add_span.find_element(By.XPATH, "..")
                add_button.click()
                time.sleep(1) 

                # Find the new input field and write the subject name
                new_subject_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='הקלד מקצוע']"))
                )
                new_subject_input.clear()
                new_subject_input.send_keys(subject_name)

                time.sleep(2) 

                subject_rows = driver.find_elements(By.CSS_SELECTOR, "div.input-data")

                #the new line we added
                new_subject_row = subject_rows[-1]

                # open the dropdown of the uints
                dropdown_toggle = new_subject_row.find_element(By.CSS_SELECTOR, "div.subject-units button.dropdown-toggle-split")
                dropdown_toggle.click()

                # choose the correct units
                units = scores[subject_name][1]
                options = new_subject_row.find_elements(By.CSS_SELECTOR, "div.subject-units .dropdown-menu a.dropdown-item")
                for option in options:
                    if option.text.strip() == str(units):
                        option.click()
                        break

                # write the grade
                grade_input = new_subject_row.find_element(By.CSS_SELECTOR, "div.subject-grade input")
                grade = scores[subject_name][0]
                grade_input.clear()
                grade_input.send_keys(str(grade))

                print(f"Set subject {subject_name} with {units} units and grade {grade}")

        # Click the "Calculate" button
    
        btn_show = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-calc")))

        btn_show.click()

        WebDriverWait(driver, 20).until(EC.url_contains("/calc-average"))


    def thirdPageOfCalculator(self,driver):  

        print("Now on page 3!")

        average_el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "grade")))

        #take the avrege that calcute 
        average = average_el.text.strip()

        time.sleep(10)

        driver.quit()
        
        return average

    # === second website ===
    def getDriver2(self):

        # service = Service(r"C:\Users\Raz Zana\Desktop\chromedriver-win64\chromedriver.exe")
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.get("https://go.huji.ac.il/?locale=he")
        time.sleep(3)

        return driver


    def firstPageOfCheckYourChance(self,degree,driver):

        admission_nav = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "admission-nav"))
        )
        # Locate the search input field

        site_option_1, site_option_2 = self.get_site_degree_options(degree)

        search_input = admission_nav.find_element(By.CLASS_NAME, "search-bar")
        search_input.clear()
        search_input.send_keys(site_option_1)

        options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-results a"))
        )

        for option in options:
            if option.text.strip() == str(site_option_1):
                option.click()
                break
            

    def secondPageOfCheckYourChance(self,driver,degree,highschool_score,psycho_scores):

        # Wait for the admission navigation bar to load
        res=False
        site_option_1, site_option_2 = self.get_site_degree_options(degree)

        WebDriverWait(driver, 10).until(
        EC.url_contains("programAdmission_")
    )
        print("Now on page 2!")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "course-fields"))
        )

        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='courseTrack']"))
        )

        select = Select(select_element)
        
        found = False
        for option in select.options:
            text = option.text.strip()
            print("🔎 Checking:", text)
            if text == site_option_2:
                print(f"✅ Selecting track: {text}")
                select.select_by_visible_text(text)
                found = True
                break

        if not found:
            print(f"❌ Track option '{site_option_2}' not found in dropdown.")

        # for option in select.options:
        #     text = option.text.strip()
        #     print("🔎 Checking:", text)
        #     if "מדעי המחשב" in text and "חד-חוגי" in text:
        #         print("✅ Selecting:", text)
        #         select.select_by_visible_text(text)
        #         break
        # else:
        #     print("❌ Option not found!")

        #grade_field = driver.find_element(By.CLASS_NAME, 'grades-fields-container')
        bagrut_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "bagrut"))
    )
        bagrut_input.clear()
        bagrut_input.send_keys(str(int(float(highschool_score))))
        time.sleep(0.2) 

        grades_field = driver.find_element(By.CLASS_NAME, 'pet-fields')

        fields = grades_field.find_elements(By.CLASS_NAME, "field")

        self.fill_psychometric_fields(fields, psycho_scores)

        # Click the "Calculate" button
        submit_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.submit.submit-SingleCourse-singleCourseResults"))
        )

        # Use JavaScript to click the button instead of direct click
        button = submit_container.find_element(By.TAG_NAME, "button")
        
        try:
            # Try JavaScript click which can work better in headless mode
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)  # Give time for scrolling
            driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            print(f"❌ Error clicking button: {e}")
            raise

        print("Clicked the submit button!")

        WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "result-msg"))
        )

        result_el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "result-msg"))
    )
        result_text = result_el.text.strip()

        url = driver.current_url

        if "לא תתאפשר קבלה" in result_text:
            return {"isAccepted": "דחייה", "url": url, "message": None}
            #  return {"isAccepted": "דחייה", "score": 0, "threshold": 0}
        else:
            return {"isAccepted": "קבלה", "url": url, "message": None}
            # return {"isAccepted": "קבלה", "score": 0, "threshold": 0}
        
        time.sleep(3)



    # === Main Code ==
    def run(self,data):
        hs_dict = data["highschool_scores"]
        degree=data["subject"]
        math= data["psycho_math"]
        total= data["psycho_score"]
        verbal= data["psycho_hebrew"]
        psycho_scores = [
            data["psycho_score"],
            data["psycho_math"],
            data["psycho_hebrew"],
            data["psycho_english"]

        ]
        res=None
        if degree not in [d["user_input"] for d in self.DEGREES_DATA]:
            msg = f"התואר '{degree}' לא קיים במערכת הקבלה של האוניברסיטה העברית. יש לבדוק את המידע באתר האוניברסיטה."
            print("❌", msg)
            
        else:
            
            driver1=self.getDriver1()
            self.firstPageOfCalculator(driver1)
            self.secondPageOfCalculator(driver1,hs_dict)
            highschool_score = self.thirdPageOfCalculator(driver1)

            print("Highschool score:", highschool_score)

            driver2=self.getDriver2()
            try:
                self.firstPageOfCheckYourChance(degree,driver2)
                res=self.secondPageOfCheckYourChance(driver2,degree,highschool_score,psycho_scores)
                print(res)
            except Exception as e:
                print(f"❌ Error in checking admission chances: {e}")
                # Take a screenshot of the current state before failing
                self.take_screenshot(driver2, "final_error")
                driver2.quit()
                raise

        if res:
            return res

        else:
            return {"isAccepted": None, "url": None, "message": msg}
# import json
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service 
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# import time
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys 
# from selenium.webdriver.support.ui import WebDriverWait, Select

# class HebrewUniversity:

#     # === Static Variables ===
#     CORE_SUBJECTS = [
#         "אזרחות",
#         "עברית: הבנה, הבעה ולשון",
#         "אנגלית",
#         "מתמטיקה",
#         "פיזיקה",
#         "ספרות",
#         "היסטוריה",
#         "תנ\"ך"
#     ]
#     DEGREES_DATA = [
#         {
#             "user_input": "מדעי המחשב",
#             "site_option_1": "מדעי המחשב",
#             "site_option_2": "מדעי המחשב, חד-חוגי"
#         },
#         {
#             "user_input": "חינוך והוראה",
#             "site_option_1": "חינוך",
#             "site_option_2": "חינוך, דו-חוגי"
#         },
#         {
#             "user_input": "מנהל עסקים",
#             "site_option_1": "מנהל עסקים",
#             "site_option_2": "מנהל עסקים,דו-חוגי"
#         },
#         {
#             "user_input": "סיעוד",
#             "site_option_1": "אחיות (סיעוד)",
#             "site_option_2": "אחיות (סיעוד), חד-חוגי, בי\"ח הדסה"
#         },
#         {
#             "user_input": "הנדסת חשמל",
#             "site_option_1": "הנדסת חשמל ומדעי המחשב או",
#             "site_option_2": "הנדסת חשמל ופיסיקה יישומית, חד-חוגי"
#         },
#         {
#             "user_input": "משפטים",
#             "site_option_1": "משפטים",
#             "site_option_2": "משפטים, חד-חוגי"
#         },
#         {
#             "user_input": "פסיכולוגיה",
#             "site_option_1": "פסיכולוגיה",
#             "site_option_2": "פסיכולוגה, דו-חוגי"
#         },
#         {
#             "user_input": "כלכלה",
#             "site_option_1": "כלכלה",
#             "site_option_2": "כלכלה, דו-חוגי"
#         },
#         {
#             "user_input": "רפואה",
#             "site_option_1": "רפואה",
#             "site_option_2": "רפואה,חד-חוגי, לימודים פרה קליניים"
#         },
#         {
#             "user_input": "עבודה סוציאלית",
#             "site_option_1": "עבודה סוציאלית",
#             "site_option_2": "עבודה סוציאלית, חד חוגי"
#         },
#         {
#             "user_input": "מתמטיקה",
#             "site_option_1": "מתמטי'ה",
#             "site_option_2": "מתמטיקה, חד חוגי"
#         },
#         {
#             "user_input": "פיזיקה",
#             "site_option_1": "פיסיקה",
#             "site_option_2": "פיסיקה, חד-חוגי"
#         },
#         {
#             "user_input": "מדעי המוח וקוגניציה" ,
#             "site_option_1": "מדעי המוח",
#             "site_option_2": "מדעי הקוגניציה והמוח, דו-חוגי"
#         },
#         {
#             "user_input": "ריפוי בעיסוק",
#             "site_option_1": "ריפוי בעיסוק",
#             "site_option_2": "ריפוי בעיסוק, חג-חוגי"
#         }
#     ]

#     SUBJECT_NAME_MAP = {
#             "תנ\"ך":"תנ\"ך",
#             "תנך": "תנ\"ך",
#             "עברית": "עברית: הבנה, הבעה ולשון",
#             "ספרות": "ספרות",
#             "אנגלית": "אנגלית",
#             "היסטוריה": "היסטוריה",
#             "אזרחות": "אזרחות",
#             "מתמטיקה": "מתמטיקה",
#             "פיזיקה": "פיזיקה"
#         }

    
#     def __init__(self, service, options):
#             self.service = service
#             self.options = options


#     def get_site_degree_options(self,user_input):

#         for item in self.DEGREES_DATA:
#             if item["user_input"] == user_input:
#                 return item["site_option_1"], item["site_option_2"]
#         return user_input, user_input  # fallback if not found



#     def calculate_psychometric_emphases(self,total,verbal, quantitative, english):
#         emphases = {
#             "verbal_emphasis": {
#                 "name": "דגש מילולי",
#                 "weights": {"verbal": 0.6, "quant": 0.2, "english": 0.2}
#             },
#             "quant_emphasis": {
#                 "name": "דגש כמותי",
#                 "weights": {"verbal": 0.2, "quant": 0.6, "english": 0.2}
#             },
#             "multi_emphasis": {
#                 "name": "דגש רב תחומי",
#                 "weights": {"verbal": 0.4, "quant": 0.4, "english": 0.2}
#             }
#         }

#         results = {}

#         for key, data in emphases.items():
#             w = data["weights"]
#             score = round(
#                 verbal * w["verbal"] +
#                 quantitative * w["quant"] +
#                 english * w["english"]
#             )
#             original_avg = (verbal + quantitative + english) / 3
#             delta = score - original_avg

#             # מקדם תיקון משוער – מעלה או מוריד מהציון הכללי לפי ההטיה
#             correction_factor = 5.33
#             emphasis_score = round(total + delta * correction_factor)

#             # הגבלה בין 200 ל־800
#             emphasis_score = max(200, min(800, emphasis_score))
#             results[key] = emphasis_score 

#         return results


#     def fill_psychometric_fields(self, fields, psycho_scores):
#         try:
#         # unpack 3 scores
#             total, quant_score, verbal_score, english_score = psycho_scores

#             # מחשבים את הדגשים
#             emphases = self.calculate_psychometric_emphases(total,verbal_score, quant_score, english_score)

#             # שמים את הדגשים בסדר: כמותי, מילולי, רב תחומי
#             emphasis_values = [
#                 emphases["quant_emphasis"],
#                 emphases["verbal_emphasis"],
#                 emphases["multi_emphasis"]
#             ]

#             for i, field in enumerate(fields):
#                 if i >= len(emphasis_values):
#                     print(f"Field #{i+1} skipped — no matching emphasis value")
#                     break

#                 value = str(int(emphasis_values[i]))

#                 input_el = field.find_element(By.TAG_NAME, "input")

#                 input_el.clear()
#                 input_el.send_keys(value)
#                 time.sleep(0.2)
#                 input_el.send_keys(Keys.TAB)
#                 time.sleep(0.2)

#                 confirmed_value = input_el.get_attribute("value")
#                 if confirmed_value.strip() != value:
#                     print(f"⚠️ Field #{i+1} lost its value, retrying...")
#                     input_el.clear()
#                     input_el.send_keys(value)
#                     input_el.send_keys(Keys.TAB)
#                     time.sleep(0.2)

#                 print(f"✅ Filled field #{i+1} with emphasis value: {value}")

#             time.sleep(2)

#         except Exception as e:
#             print(f"❌ Error in fill_psychometric_fields: {e}")


#     # === first website ===
#     def getDriver1(self):    
        
#         # driver = webdriver.Chrome(service=self.service)
#         driver = webdriver.Chrome(service=self.service, options=self.options)

#         driver.get("https://bagrut-calculator.huji.ac.il/calculator/#/grade-input")

#         time.sleep(3)

#         return driver


#     def firstPageOfCalculator(self, driver):    

#         btn_group = driver.find_element(By.CLASS_NAME, "btn-group")

#         # Find all buttons inside the group
#         buttons = btn_group.find_elements(By.TAG_NAME, "button")

#         # Click the SECOND button (index 1)
#         if len(buttons) > 1:
#             buttons[1].click()
#         else:
#             print("Second button not found!")

#         first_item = driver.find_elements(By.CLASS_NAME, "dropdown-item")[0]
#         first_item.click()

#         #click the "Next" button
#         btn_show = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CLASS_NAME, "btn-show")))

#         btn_show.click()

#         WebDriverWait(driver, 10).until(EC.url_contains("/grade-input"))

    
#     def secondPageOfCalculator(self, driver,scores):

#         print("Now on page 2!")

#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.subject-title span")))
        
#         #Find and print subject names
#         subject_rows = driver.find_elements(By.CSS_SELECTOR, 'div.input-data')
        
#         for i, line in enumerate(subject_rows):
#             # Check if the line contains an input element (indicating it's a subject row)  
#             if (line.find_elements(By.TAG_NAME, "input")):

#                 subject_name_el = line.find_element(By.CSS_SELECTOR, 'div.subject-title span')
#                 subject_name = subject_name_el.text.strip()

#                 print(f"Subject #{i + 1}: {subject_name}")

#                 normalized_name = self.SUBJECT_NAME_MAP.get(subject_name, subject_name)

#                 if normalized_name not in scores:
#                     print(f"⚠️ Subject '{subject_name}' (mapped to '{normalized_name}') was not found in the input JSON")
#                     continue

#                 #take from the json   
#                 # here to change i need to make a map from subjectname to the json 

#                 grade = scores[normalized_name][0]
#                 inits= scores[normalized_name][1]

#                 # Enter units  for the subject

#                 #click in the dropdown
#                 dropdown_toggle = line.find_element(By.CSS_SELECTOR, "div.subject-units button.dropdown-toggle-split")
#                 dropdown_toggle.click()

#                 #the options in the dropdown
#                 options = line.find_elements(By.CSS_SELECTOR, "div.subject-units .dropdown-menu a.dropdown-item")
#                 for option in options:
#                     if option.text.strip() == str(inits):
#                         option.click()
#                         break

#                 #write the grade
#                 input_grade = line.find_element(By.CSS_SELECTOR, 'div.subject-grade input')
#                 input_grade.clear()
#                 input_grade.send_keys(str(grade))

#         #add more subjects
#         for subject_name in scores.keys():
#             if subject_name not in self.CORE_SUBJECTS:
#                 print(f"Adding new subject: {subject_name}")

#                 add_span = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'הוסף מקצוע')]"))
#             )
#                 add_button = add_span.find_element(By.XPATH, "..")
#                 add_button.click()
#                 time.sleep(1) 

#                 # Find the new input field and write the subject name
#                 new_subject_input = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='הקלד מקצוע']"))
#                 )
#                 new_subject_input.clear()
#                 new_subject_input.send_keys(subject_name)

#                 time.sleep(2) 

#                 subject_rows = driver.find_elements(By.CSS_SELECTOR, "div.input-data")

#                 #the new line we added
#                 new_subject_row = subject_rows[-1]

#                 # open the dropdown of the uints
#                 dropdown_toggle = new_subject_row.find_element(By.CSS_SELECTOR, "div.subject-units button.dropdown-toggle-split")
#                 dropdown_toggle.click()

#                 # choose the correct units
#                 units = scores[subject_name][1]
#                 options = new_subject_row.find_elements(By.CSS_SELECTOR, "div.subject-units .dropdown-menu a.dropdown-item")
#                 for option in options:
#                     if option.text.strip() == str(units):
#                         option.click()
#                         break

#                 # write the grade
#                 grade_input = new_subject_row.find_element(By.CSS_SELECTOR, "div.subject-grade input")
#                 grade = scores[subject_name][0]
#                 grade_input.clear()
#                 grade_input.send_keys(str(grade))

#                 print(f"Set subject {subject_name} with {units} units and grade {grade}")

#         # Click the "Calculate" button
    
#         btn_show = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.CLASS_NAME, "btn-calc")))

#         btn_show.click()

#         WebDriverWait(driver, 20).until(EC.url_contains("/calc-average"))


#     def thirdPageOfCalculator(self,driver):  

#         print("Now on page 3!")

#         average_el = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, "grade")))

#         #take the avrege that calcute 
#         average = average_el.text.strip()

#         time.sleep(10)

#         driver.quit()
        
#         return average

#     # === second website ===
#     def getDriver2(self):

#         # service = Service(r"C:\Users\Raz Zana\Desktop\chromedriver-win64\chromedriver.exe")
#         driver = webdriver.Chrome(service=self.service, options=self.options)
#         driver.get("https://go.huji.ac.il/?locale=he")
#         time.sleep(3)

#         return driver


#     def firstPageOfCheckYourChance(self,degree,driver):

#         admission_nav = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "admission-nav"))
#         )
#         # Locate the search input field

#         site_option_1, site_option_2 = self.get_site_degree_options(degree)

#         search_input = admission_nav.find_element(By.CLASS_NAME, "search-bar")
#         search_input.clear()
#         search_input.send_keys(site_option_1)

#         options = WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-results a"))
#         )

#         for option in options:
#             if option.text.strip() == str(site_option_1):
#                 option.click()
#                 break
            

#     def secondPageOfCheckYourChance(self,driver,degree,highschool_score,psycho_scores):

#         # Wait for the admission navigation bar to load
#         res=False
#         site_option_1, site_option_2 = self.get_site_degree_options(degree)

#         WebDriverWait(driver, 10).until(
#         EC.url_contains("programAdmission_")
#     )
#         print("Now on page 2!")
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "course-fields"))
#         )

#         select_element = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='courseTrack']"))
#         )

#         select = Select(select_element)
        
#         found = False
#         for option in select.options:
#             text = option.text.strip()
#             print("🔎 Checking:", text)
#             if text == site_option_2:
#                 print(f"✅ Selecting track: {text}")
#                 select.select_by_visible_text(text)
#                 found = True
#                 break

#         if not found:
#             print(f"❌ Track option '{site_option_2}' not found in dropdown.")

#         # for option in select.options:
#         #     text = option.text.strip()
#         #     print("🔎 Checking:", text)
#         #     if "מדעי המחשב" in text and "חד-חוגי" in text:
#         #         print("✅ Selecting:", text)
#         #         select.select_by_visible_text(text)
#         #         break
#         # else:
#         #     print("❌ Option not found!")

#         #grade_field = driver.find_element(By.CLASS_NAME, 'grades-fields-container')
#         bagrut_input = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.NAME, "bagrut"))
#     )
#         bagrut_input.clear()
#         bagrut_input.send_keys(str(int(float(highschool_score))))
#         time.sleep(0.2) 

#         grades_field = driver.find_element(By.CLASS_NAME, 'pet-fields')

#         fields = grades_field.find_elements(By.CLASS_NAME, "field")

#         self.fill_psychometric_fields(fields, psycho_scores)

#         # Click the "Calculate" button
#         submit_container = WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "div.submit.submit-SingleCourse-singleCourseResults"))
#         )

#         button = submit_container.find_element(By.TAG_NAME, "button")

#         button.click()

#         print("Clicked the submit button!")

#         WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "result-msg"))
#         )

#         result_el = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "result-msg"))
#     )
#         result_text = result_el.text.strip()

#         url = driver.current_url

#         if "לא תתאפשר קבלה" in result_text:
#             return {"isAccepted": "דחייה", "url": url, "message": None}
#             #  return {"isAccepted": "דחייה", "score": 0, "threshold": 0}
#         else:
#             return {"isAccepted": "קבלה", "url": url, "message": None}
#             # return {"isAccepted": "קבלה", "score": 0, "threshold": 0}
        
#         time.sleep(3)



#     # === Main Code ==
#     def run(self,data):
#         hs_dict = data["highschool_scores"]
#         degree=data["subject"]
#         math= data["psycho_math"]
#         total= data["psycho_score"]
#         verbal= data["psycho_hebrew"]
#         psycho_scores = [
#             data["psycho_score"],
#             data["psycho_math"],
#             data["psycho_hebrew"],
#             data["psycho_english"]

#         ]
#         res=None
#         if degree not in [d["user_input"] for d in self.DEGREES_DATA]:
#             msg = f"התואר '{degree}' לא קיים במערכת הקבלה של האוניברסיטה העברית. יש לבדוק את המידע באתר האוניברסיטה."
#             print("❌", msg)
            
#         else:
            
#             driver1=self.getDriver1()
#             self.firstPageOfCalculator(driver1)
#             self.secondPageOfCalculator(driver1,hs_dict)
#             highschool_score = self.thirdPageOfCalculator(driver1)

#             print("Highschool score:", highschool_score)

#             driver2=self.getDriver2()
#             self.firstPageOfCheckYourChance(degree,driver2)
#             res=self.secondPageOfCheckYourChance(driver2,degree,highschool_score,psycho_scores)
#             print(res)

#         if res:
#             return res

#         else:
#             return {"isAccepted": None, "url": None, "message": msg}




