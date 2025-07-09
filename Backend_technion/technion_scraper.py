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
    # Dictionary of valid Technion degrees with their required admission scores
    valid_technion_degrees = {
        "אדריכלות נוף": 83,
        "ארכיטקטורה": 85,
        "ביולוגיה": 83,
        "ביולוגיה וכימיה (דו-חוגי)": 83,
        "הנדסה אזרחית": 87,
        "הנדסה ביוכימית": 85,
        "הנדסה ביוטכנולוגיה ומזון": 84,
        "הנדסה ביו-רפואית": 87,
        "הנדסה ביו-רפואית ופיזיקה": 88,
        "הנדסה אווירונוטיקה וחלל": 86,
        "הנדסת אווירונוטיקה וחלל ופיזיקה": 86,
        "הנדסת הסביבה": 83,
        "הנדסת חומרים": 86,
        "הנדסת חומרים וביולוגיה": 86,
        "הנדסת חומרים וכימיה": 86,
        "הנדסת חומרים ופיזיקה": 86,
        "הנדסת חשמל": 91,
        "הנדסת חשמל ופיזיקה": 92,
        "הנדסת חשמל-מתמטיקה": 92,
        "הנדסה כימית": 84,
        "הנדסת מחשבים": 91,
        "הנדסת מיפוי וגיאו-אינפורמציה": 83,
        "הנדסת מכונות": 87,
        "הנדסת מערכות מידע": 89,
        "הנדסת נתונים ומידע": 91,
        "הנדסת תוכנה": 91,
        "הנדסת תעשיה וניהול": 89,
        "חינוך למדע וטכנולוגיה (תואר ראשון)": 84,
        "חינוך למדע וטכנולוגיה-מדעי המחשב (תואר ראשון)": 87,
        "כימיה": 83,
        "מדעי המחשב": 91,
        "מדעי המחשב ומתמטיקה": 91,
        "מדעי המחשב ופיזיקה": 91,
        "מתמטיקה": 87,
        "מתמטיקה עם מדעי המחשב": 87,
        "מתמטיקה יישומית": 87,
        "מתמטיקה – פיזיקה": 87,
        "פיזיקה": 85,
        "מדעי הרפואה-מגמת רפואה": 91.270,
        "מדעי הרפואה - הנדסה ביו-רפואית (תואר כפול)": 91.270,
        "מדעי הרפואה – מדעי המחשב (תואר כפול)": 91.270
    }


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
        "רפואה": "מדעי הרפואה-מגמת רפואה"
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

    def __init__(self, options):
        self.service = Service(ChromeDriverManager().install())
        self.options = options

    # This method will be executed when the thread starts
    def run(self, data):
        # Define default values
        msg = ""
        url = "https://admissions.technion.ac.il/sechem-for-admission/sekem/"
        # Check if requested_degree exists in inputJson, if not, use degree
        if "requested_degree" not in data and "degree" in data:
            data["requested_degree"] = data["degree"]
        
        requested_degree = data["requested_degree"]
        if requested_degree in self.degree_alternative_name_dict:
            technion_degree = self.degree_alternative_name_dict[requested_degree]
            # If the mapped degree is None, it means this degree doesn't exist in Technion
            if technion_degree is None:
                return {"isAccepted": None, "url": url, "message": f"תואר {requested_degree} לא קיים בטכניון"}
        else:
            technion_degree = requested_degree
        
        # Check if the degree exists in the valid Technion degrees list
        if technion_degree not in self.valid_technion_degrees:
            return {"isAccepted": None, "url": url, "message": f"תואר {requested_degree} לא קיים בטכניון"}
        
        calculated_sum, error_message = self.get_tech_match_score(data)
        
        # If there's an error message, return rejection with the message
        if error_message:
            if "דחייה בגלל מספר יחידות לא מספק" in error_message:
                 isAccepted = "דחייה"
            else:
                isAccepted = None
            return {
                "isAccepted": isAccepted,
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
        driver = webdriver.Chrome(service=self.service, options=self.options)
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
                hs_dict[technion_subject] = values
            else:
                hs_dict[subject] = values

        try:
            # Set up to handle unexpected alerts
            driver.execute_script("window.onbeforeunload = function(e){};")
            
            # Wait for form to load
            form = wait.until(EC.presence_of_element_located((By.NAME, "sehem_table")))
            tech_calc = WebDriverWait(form, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "technion-calculator"))
            )

            # Wait and click the "bagrotYes" button
            # click_button = WebDriverWait(tech_calc, 10).until(
            #     EC.element_to_be_clickable((By.ID, "bagrotYes"))
            # )
            # driver.execute_script("arguments[0].scrollIntoView(true);", click_button)
            # time.sleep(1)  # give time for scroll to settle
            # click_button.click()
            bagrot_radio = driver.find_element(By.ID, "bagrotYes")
            driver.execute_script("arguments[0].click();", bagrot_radio)
            # Wait for the mandatory table to be visible
            bagrut_form = WebDriverWait(tech_calc, 10).until(
                EC.presence_of_element_located((By.ID, "bagrotForm"))
            )
            
            tables = WebDriverWait(bagrut_form, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "two-column-table"))
            )
            lines = []
            for table in tables:
                table_name = WebDriverWait(table, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sub-title"))
                )
                tbody = WebDriverWait(table, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "tbody"))
                )
                rows = tbody.find_elements(By.TAG_NAME, "tr")
                lines.extend(rows)

            for line in lines:
                try:
                    subject_th = WebDriverWait(line, 20).until(
                        EC.visibility_of_element_located((By.XPATH, "./th[@id]"))
                    )
                    if subject_th.is_displayed():
                        subject_name = subject_th.text
                    else:
                        # Use JavaScript to get the text content if the element is not visible
                        subject_name = driver.execute_script("return arguments[0].textContent;", subject_th).strip()
                    if subject_name in hs_dict:
                        score, units = hs_dict[subject_name]
                        td_elements = line.find_elements(By.TAG_NAME, "td")
                        if len(td_elements) >= 2:
                            dropdown_td = td_elements[0]
                            input_td = td_elements[1]

                            dropdown_menu = dropdown_td.find_elements(By.TAG_NAME, "select")
                            if dropdown_menu:
                                # Wait for the element to be both present AND interactable
                                dropdown_menu = WebDriverWait(line, 10).until(
                                    EC.element_to_be_clickable((By.TAG_NAME, "select"))
                                )
                                
                                # Scroll the element into view before interacting
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_menu)
                                time.sleep(0.5)  # Give time for scroll to complete
                                
                                select = Select(dropdown_menu)

                                # For all subjects
                                if ((subject_name == "אנגלית" or subject_name == "מתמטיקה") and int(units) < 4):
                                    driver.quit()
                                    subject_hebrew = "אנגלית" if subject_name == "אנגלית" else "מתמטיקה"
                                    return None, f"דחייה בגלל מספר יחידות לא מספק ב{subject_hebrew}. בטכניון נדרש מינימום 4 יחידות."
                                select.select_by_value(units)
                            else:
                                self.exit(driver, "Missing dropdown")
                            
                            score_input = input_td.find_elements(By.TAG_NAME, "input")
                            if score_input:
                                score_input[0].clear()
                                score_input[0].send_keys(score)
                            else:
                                self.exit(driver, "Missing input field")
                            time.sleep(1)
                            
                            # Remove the subject from hs_dict after processing it
                            del hs_dict[subject_name]
                        else:
                            self.exit(driver, "Insufficient <td> elements")
                        
                except Exception as e:
                    raise Exception("מקצועות חובה לא הופיעו")

            
            miktzoaBhira_section = bagrut_form.find_element(By.CLASS_NAME, "four-column-table")
            tbody = miktzoaBhira_section.find_element(By.TAG_NAME, "tbody")
            miktzoot = tbody.find_elements(By.TAG_NAME, "tr")
            time.sleep(1)
            idx = 1
            for hs_miktzoa, (grade, unit) in hs_dict.items():
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
                            try:
                                    select_subject.select_by_visible_text("מקצוע אחר שאינו ברשימה")
                            except NoSuchElementException:
                                            # Handle the case when "מקצוע אחר שאינו ברשימה" is not found in the dropdown
                                            # You can choose to skip this subject or take any other appropriate action
                                            raise Exception("מקצוע אחר שאינו ברשימה לא הופיע")
                    
                    # Find and set the units
                    # Try to find and interact with the dropdown using standard Selenium approach
                    try:
                        # Wait for the dropdown to be clickable
                        units_dropdown = WebDriverWait(miktzoa_row, 10).until(
                            EC.element_to_be_clickable((By.ID, f"y{idx}"))
                        )
                        
                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", units_dropdown)
                        time.sleep(0.5)  # Give time for scroll to complete
                        
                        # Try standard Select approach
                        select_units = Select(units_dropdown)
                        select_units.select_by_value(unit)
                        
                    except Exception as e:
                        print(f"Standard unit select failed, trying JavaScript fallback: {str(e)}")
                        
                        # JavaScript fallback approach
                        js_script = f"""
                        var select = document.getElementById('y{idx}');
                        if(select) {{
                            select.value = '{unit}';
                            
                            // Create and dispatch change event
                            var event = new Event('change', {{ bubbles: true }});
                            select.dispatchEvent(event);
                            return true;
                        }}
                        return false;
                        """
                        
                        success = driver.execute_script(js_script)
                        if not success:
                            print(f"JavaScript fallback also failed for dropdown y{idx}")
                            raise

                    
                    # Find and set the score
                    score_input = miktzoa_row.find_element(By.ID, f"G_{idx}")
                    score_input.clear()
                    score_input.send_keys(grade)
                    
                    idx += 1
                    
                    # Check if there are more subjects to add
                    if idx <= len(miktzoot):
                            # Click the "Add" button to add more subjects
                            add_button = miktzoa_row.find_element(By.CSS_SELECTOR, "button.add_bhira")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", add_button)
                            # Wait for the new row to be added
                            time.sleep(1)
            
            try:
                # Wait for the element to be clickable (both visible and enabled)
                psychometry_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "psychometry"))
                )
                
                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", psychometry_input)
                time.sleep(0.5)  # Give time for scroll to complete
                
                
                # Try standard approach first
                try:
                    psychometry_input.clear()
                    psychometry_input.send_keys(str(psycho_score))  # Convert to string to be safe
                except Exception as e:
                    print(f"Standard psychometry input failed, trying JavaScript fallback: {str(e)}")
                    
                    # JavaScript fallback for both clearing and entering text
                    js_script = f"""
                    var input = document.getElementById('psychometry');
                    if(input) {{
                        input.value = '';  // Clear first
                        input.value = '{psycho_score}';  // Set new value
                        
                        // Create and dispatch input event
                        var event = new Event('input', {{ bubbles: true }});
                        input.dispatchEvent(event);
                        
                        // Also dispatch change event
                        var changeEvent = new Event('change', {{ bubbles: true }});
                        input.dispatchEvent(changeEvent);
                        
                        return true;
                    }}
                    return false;
                    """
                    
                    success = driver.execute_script(js_script)
                    if not success:
                        print("JavaScript fallback also failed for psychometry input")
                    
            except Exception as e:
                print(f"Failed to interact with psychometry input: {str(e)}")
                raise

            # Wait for the "חישוב סכם" button to be visible
            calculate_button_selector = 'input[value="חישוב סכם"]'
            calculate_button = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, calculate_button_selector))
            )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calculate_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", calculate_button)
            
            # Handle both types of popups that might appear
            try:
                # First check for browser alert (this is what's causing the error)
                alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
                if alert:
                    alert_text = alert.text
                    alert.accept() 
            except TimeoutException:
                
                try:
                    popup = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ui-dialog"))
                    )
                    popup_text = popup.find_element(By.CLASS_NAME, "ui-dialog-content").text
                    if "4 יחידות" in popup_text and "מתמטיקה" in popup_text:
                        ok_button = popup.find_element(By.CLASS_NAME, "ui-button")
                        driver.execute_script("arguments[0].click();", ok_button)
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
                driver.quit()
                return calculated_sum, None
            else:
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
            raise Exception("שגיאה בחישוב הסכם - אירעה בעיה בטיפול בהתראה")
        except Exception as e:
            print(f"Failed to load form or interact with page: {e}")
            driver.quit()
            raise Exception("שגיאה בחישוב הסכם - אירעה בעיה בטעינת הטופס")

    def check_if_accepted(self, calculated_sum, inputJson):
        if calculated_sum is None:
            return None, "לא ניתן לחשב את הסכם שלך"
        requested_degree = inputJson["requested_degree"]
        if requested_degree in self.degree_alternative_name_dict:
            requested_degree = self.degree_alternative_name_dict[requested_degree]
        required_sum = self.valid_technion_degrees[requested_degree]
        if (required_sum > calculated_sum):
            return "דחייה", None
        else:
            return "קבלה", None


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
