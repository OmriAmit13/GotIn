from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException

import time
import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

class TechnionUniversity():

    ### Static Variables ###

    # Dictionary to map website degree names to Technion degree names
    degree_alternative_name_dict = {
        "הנדסה אזרחית": "הנדסה אזרחית",
        "הנדסה ביוטכנולוגית": "הנדסה ביוטכנולוגית ומזון",
        "הנדסה ביורפואית": "הנדסה ביו-רפואית",
        "הנדסה תעשייה וניהול": "הנדסת תעשיה וניהול",
        "חינוך והוראה": None,
        "מנהל עסקים": None,
        "משפטים": None,
        "עבודה סוציאלית": None,
        "רפואה": "מדעי הרפואה-מגמת רפואה",
    }

    # Dictionary to map high school subject names from website to Technion names
    highschool_subject_name_dict = {
        "עברית: הבנה, הבעה ולשון": "עברית (הבעה)"	,
        "היסטוריה": "היסטוריה / תולדות עם ישראל",
        "ספרות": "ספרות עברית",
        "אזרחות": "אזרחות",
        'תנ"ך': 'תנ"ך',
        "ביולוגיה": "ביולוגיה",
        "כימיה": "כימיה",
        "פיזיקה": "פיזיקה",
        "מדעי המחשב": "מדעי המחשב",
        "היסטוריה של עם ישראל": "היסטוריה / תולדות עם ישראל",
        "גיאוגרפיה": "גיאוגרפיה",
        "סוציולוגיה": "סוציולוגיה",
        "פסיכולוגיה": "פסיכולוגיה",
        "מדעי החברה": "מדעי החברה",
        "ערבית (ליהודים)": "ערבית",
        "צרפתית": "צרפתית",
        "רוסית": "רוסית",
        "אמנות חזותית": "אמנות",
        "מוזיקה": "מוזיקה",
        "תיאטרון": "תיאטרון",
        "קולנוע": "קולנוע",
        "מחול": "מחול",
        "חינוך גופני": "חינוך גופני",
        "מחשבת ישראל": "מחשבת ישראל",
        "תושב\"ע": "תלמוד / תושב\"ע",
        "תלמוד": "תלמוד / תושב\"ע"
    }

    def __init__(self, service, options):
        self.service = service
        self.options = options

    # This method will be executed when the thread starts
    def run(self, data):
        # Define default values
        msg = ""
        url = "https://admissions.technion.ac.il/sechem-for-admission/sekem/"
        
        calculated_sum, error_message = self.get_tech_match_score(data)
        
        # If there's an error message, return rejection with the message
        if error_message:
            if "דחייה בגלל מספר יחידות לא מספק" in error_message:
                 isAccepted = "דחייה"
            else:
                isAccepted = None
            return {
                "isAccepted": None,
                "url": url,
                "message": error_message
            }
            
        result, message = self.check_if_accepted(calculated_sum, data)
        return {
            "isAccepted": result,
            "url": url,
            "message": message
        }

    def get_tech_match_score(self, inputJson):
        #driver = webdriver.Chrome(service=self.service, options=self.options)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        wait = WebDriverWait(driver, 10)
        driver.get("https://admissions.technion.ac.il/calculator/")

        psycho_score = inputJson["psycho_score"]
        
        # Map high school subject names to Technion names
        hs_dict_original = inputJson["highschool_scores"]
        
        # Check if requested_degree exists in inputJson, if not, use degree
        if "requested_degree" not in inputJson and "degree" in inputJson:
            inputJson["requested_degree"] = inputJson["degree"]
            
        hs_dict = {}
        
        for subject, values in hs_dict_original.items():
            if subject in self.highschool_subject_name_dict:
                technion_subject = self.highschool_subject_name_dict[subject]
                print(f"Mapped subject '{subject}' to '{technion_subject}'")
                hs_dict[technion_subject] = values
            else:
                print(f"Using original subject name: '{subject}'")
                hs_dict[subject] = values

        try:
            # Set up to handle unexpected alerts
            driver.execute_script("window.onbeforeunload = function(e){};")
            
            # Wait for form to load
            form = wait.until(EC.presence_of_element_located((By.NAME, "sehem_table")))
            tech_calc = form.find_element(By.CLASS_NAME, "technion-calculator")

            # Wait and click the "bagrotYes" button
            click_button = WebDriverWait(tech_calc, 10).until(
                EC.element_to_be_clickable((By.ID, "bagrotYes"))
            )
            click_button.click()

            # Wait for the mandatory table to be visible
            bagrut_form = WebDriverWait(tech_calc, 10).until(
                EC.presence_of_element_located((By.ID, "bagrotForm"))
            )
            
            tables = bagrut_form.find_elements(By.CLASS_NAME, "two-column-table")
            lines = []
            for table in tables:
                print(f"table: {table}")
                print(f"table name: {table.find_element(By.CLASS_NAME, 'sub-title').text.strip()}")
                tbody = table.find_element(By.TAG_NAME, "tbody")
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                lines.extend(rows)

            time.sleep(2)
            for line in lines:
                try:
                    subject_name_element = line.find_element(By.TAG_NAME, "th")
                    subject_name = subject_name_element.text.strip()
                    print(f"Subject found: {subject_name}")
                    if subject_name in hs_dict:
                        score, units = hs_dict[subject_name]
                        td_elements = line.find_elements(By.TAG_NAME, "td")
                        if len(td_elements) >= 2:
                            dropdown_td = td_elements[0]
                            input_td = td_elements[1]

                            dropdown_menu = dropdown_td.find_elements(By.TAG_NAME, "select")
                            if dropdown_menu:
                                print("entered drop down try")
                                dropdown_menu = line.find_element(By.TAG_NAME, "select")
                                select = Select(dropdown_menu)
                                
                                # For all subjects
                                if ((subject_name == "אנגלית" or subject_name == "מתמטיקה") and int(units) < 4):
                                    driver.quit()
                                    subject_hebrew = "אנגלית" if subject_name == "אנגלית" else "מתמטיקה"
                                    return None, f"דחייה בגלל מספר יחידות לא מספק ב{subject_hebrew}. בטכניון נדרש מינימום 4 יחידות."
                                select.select_by_value(units)
                            else:
                                print(f"No dropdown menu found for subject: {subject_name}")
                                self.exit(driver, "Missing dropdown")
                            
                            score_input = input_td.find_elements(By.TAG_NAME, "input")
                            if score_input:
                                score_input[0].clear()
                                score_input[0].send_keys(score)
                            else:
                                print(f"No input field found for subject: {subject_name}")
                                self.exit(driver, "Missing input field")
                            time.sleep(1)
                            
                            # Remove the subject from hs_dict after processing it
                            del hs_dict[subject_name]
                            print(f"Removed {subject_name} from hs_dict after processing")
                        else:
                            print(f"Insufficient <td> elements found for subject: {subject_name}")
                            self.exit(driver, "Insufficient <td> elements")
                        
                except Exception as e:
                    print(f"Error processing row: {e}")

            
            miktzoaBhira_section = bagrut_form.find_element(By.CLASS_NAME, "four-column-table")
            tbody = miktzoaBhira_section.find_element(By.TAG_NAME, "tbody")
            miktzoot = tbody.find_elements(By.TAG_NAME, "tr")
            time.sleep(1)
            idx = 1
            for hs_miktzoa, (grade, unit) in hs_dict.items():
                    print(f"Adding additional subject: {hs_miktzoa}, Score: {grade}, Units: {unit}")
                    time.sleep(1)
                    # Find the row for the current index
                    miktzoa_row = miktzoaBhira_section.find_element(By.ID, f"bhira{idx}")
                    time.sleep(1)
                    # Find the dropdown for subject selection
                    subject_dropdown = miktzoa_row.find_element(By.NAME, f"mikztootBhira_{idx}")
                    select_subject = Select(subject_dropdown)
                    try:
                            select_subject.select_by_visible_text(hs_miktzoa)
                    except NoSuchElementException:
                            print(f"Subject '{hs_miktzoa}' not found in the dropdown. Selecting 'מקצוע אחר שאינו ברשימה'.")
                            try:
                                    select_subject.select_by_visible_text("מקצוע אחר שאינו ברשימה")
                            except NoSuchElementException:
                                            print("Option 'מקצוע אחר שאינו ברשימה' not found in the dropdown.")
                                            # Handle the case when "מקצוע אחר שאינו ברשימה" is not found in the dropdown
                                            # You can choose to skip this subject or take any other appropriate action
                                            continue
                    
                    # Find and set the units
                    units_dropdown = miktzoa_row.find_element(By.ID, f"y{idx}")
                    select_units = Select(units_dropdown)
                    select_units.select_by_value(unit)
                    
                    # Find and set the score
                    score_input = miktzoa_row.find_element(By.ID, f"G_{idx}")
                    score_input.clear()
                    score_input.send_keys(grade)
                    
                    idx += 1
                    
                    # Check if there are more subjects to add
                    if idx <= len(miktzoot):
                            # Click the "Add" button to add more subjects
                            add_button = miktzoa_row.find_element(By.CSS_SELECTOR, "button.add_bhira")
                            add_button.click()
                            # Wait for the new row to be added
                            time.sleep(1)
            
            psychometry_input = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "psychometry"))
            )
            print("psychometry")
            time.sleep(1)
            psychometry_input.clear()
            time.sleep(1)
            psychometry_input.send_keys(psycho_score)
            time.sleep(1)

            # Wait for the "חישוב סכם" button to be visible
            calculate_button_selector = 'input[value="חישוב סכם"]'
            calculate_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, calculate_button_selector))
            )

            # Click the "חישוב סכם" button
            calculate_button.click()
            
            # Handle both types of popups that might appear
            try:
                # First check for browser alert (this is what's causing the error)
                alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
                if alert:
                    alert_text = alert.text
                    print(f"Alert detected: {alert_text}")
                    alert.accept()  # Click OK on the alert
                    print("Clicked OK on alert")
            except TimeoutException:
                print("No browser alert appeared")
                
                # Then check for UI dialog popup
                try:
                    popup = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ui-dialog"))
                    )
                    popup_text = popup.find_element(By.CLASS_NAME, "ui-dialog-content").text
                    if "4 יחידות" in popup_text and "מתמטיקה" in popup_text:
                        print("Detected 4-unit math warning popup")
                        ok_button = popup.find_element(By.CLASS_NAME, "ui-button")
                        ok_button.click()
                        print("Clicked OK on 4-unit math popup")
                except TimeoutException:
                    print("No UI dialog popup appeared")
            
            # Wait for the new page to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "one_line_results")))
            # Find and extract the calculated sum from the new page
            calculated_sum_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'הסכם לדיוני הקבלה')]")
            # Extract the text
            text = calculated_sum_element.text

            # Use regex to extract the number
            match = re.search(r"([\d.]+)$", text)
            if match:
                calculated_sum = float(match.group(1))
                print("Extracted number:", calculated_sum)
                driver.quit()
                return calculated_sum, None
            else:
                print("No number found.")
                driver.quit()
                return None, "לא ניתן לחשב את הסכם שלך"

        except UnexpectedAlertPresentException as alert_error:
            try:
                # Handle unexpected alert
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"Handling unexpected alert: {alert_text}")
                alert.accept()
                
                # Try to continue after accepting the alert
                try:
                    # Wait for the results page to load
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "one_line_results")))
                    calculated_sum_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'הסכם לדיוני הקבלה')]")
                    text = calculated_sum_element.text
                    match = re.search(r"([\d.]+)$", text)
                    if match:
                        calculated_sum = float(match.group(1))
                        print("Extracted number after handling alert:", calculated_sum)
                        driver.quit()
                        return calculated_sum
                except Exception:
                    print("Could not continue after handling alert")
            except Exception as e:
                print(f"Failed to handle alert: {e}")
            driver.quit()
            return None, "שגיאה בחישוב הסכם - אירעה בעיה בטיפול בהתראה"
        except Exception as e:
            print(f"Failed to load form or interact with page: {e}")
            driver.quit()
            return None, "שגיאה בחישוב הסכם - אירעה בעיה בטעינת הטופס"

    def check_if_accepted(self, calculated_sum, inputJson):
        if calculated_sum is None:
            return None, "לא ניתן לחשב את הסכם שלך"
            
        driver = webdriver.Chrome(service=self.service, options=self.options)
        driver.get("https://admissions.technion.ac.il/sechem-for-admission/sekem/")
        time.sleep(2)

        try:
            # Click the accordion label
            accordion_button = driver.find_element(By.ID, "fl-accordion-j5qntrlu9hwf-label-0")
            accordion_button.click()

            # Optional: Wait and verify that content expanded
            time.sleep(1)
            
            # Get the requested degree and map it to Technion degree name if needed
            requested_degree = inputJson["requested_degree"]
            if requested_degree in self.degree_alternative_name_dict:
                technion_degree = self.degree_alternative_name_dict[requested_degree]
                # If the mapped degree is None, it means this degree doesn't exist in Technion
                if technion_degree is None:
                    driver.quit()
                    return None, f"תואר {requested_degree} לא קיים בטכניון"
                print(f"Mapped '{requested_degree}' to '{technion_degree}'")
            else:
                technion_degree = requested_degree
                print(f"Using original degree name: '{technion_degree}'")
                
            accordion_content = driver.find_element(By.ID, "fl-accordion-j5qntrlu9hwf-panel-0")
            tbody = accordion_content.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            found = False
            for row in rows:
                # Find all the cells within the row
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                
                # Check if the row contains the target degree
                if technion_degree in cells[0].text:
                    # Extract the סכם נדרש לקבלה value from the corresponding cell
                    required_sum = float(cells[2].text)
                    print(f"Degree: {technion_degree}")
                    time.sleep(1)
                    found = True
                    if (required_sum > calculated_sum):
                        print(f"You didn't get in :(. \n Required Sum: {required_sum} \n Your Sum: {calculated_sum}")
                        driver.quit()
                        return "דחייה", None
                    else:
                        print(f"You got in! :) \n Required Sum: {required_sum} \n Your Sum: {calculated_sum}")
                        driver.quit()
                        return "קבלה", None
            
            if not found:        
                print(f"Degree '{technion_degree}' not found in the table.")
                driver.quit()
                return None, f"תואר {requested_degree} לא קיים בטכניון"                
        except Exception as e:
            print(f"Error checking acceptance: {e}")
            driver.quit()
            return None, f"שגיאה בבדיקת הקבלה: {str(e)}"

    def exit(self, driver, exit_msg):
        print(exit_msg)
        driver.quit()

if __name__ == '__main__':
    service = Service("/Users/ophirp/Downloads/chromedriver-mac-arm64/chromedriver")
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    uni = TechnionUniversity(service, options)

    # Load the input JSON file
    with open("input.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    start_time = time.time()
    result = uni.run(data)
    end_time = time.time()
    
    print(result)
    print(f"Execution time: {end_time - start_time} seconds")