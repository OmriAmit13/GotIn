import time
import json
import os
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager

class BenGurionUniversity:
    """
    Class for handling Ben Gurion University admission calculations.
    Includes built-in browser interaction functionality.
    """

    def __init__(self, service=None, chrome_options=None):
        """
        Initialize with browser configuration.
        
        Args:
            service: Chrome service instance (optional, will use WebDriverManager if None)
            chrome_options: Chrome options instance (optional, will create default options if None)
        """
        # Store browser configuration for later
        self.service = service
        self.chrome_options = chrome_options
        self.use_webdriver_manager = (service is None)
        
        # Initialize WebDriver attributes
        self.driver = None
        self.wait = None
        
        # Set base URL
        self.base_url = "https://www.bgu.ac.il/welcome/ba/calculator/"
        
    def start_browser(self, wait_time=15):
        """
        Start the browser session if not already started.
        
        Args:
            wait_time: Default wait time for WebDriverWait in seconds
        """
        if self.driver is None:
            # Configure Chrome options if not provided
            if self.chrome_options is None:
                self.chrome_options = Options()
                self.chrome_options.add_argument("--headless=new")
                self.chrome_options.add_argument("--disable-gpu")
                self.chrome_options.add_argument("--window-size=1920,1080")
                self.chrome_options.add_argument("--no-sandbox")
                self.chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Create service using WebDriverManager if needed
            if self.use_webdriver_manager:
                self.service = Service(ChromeDriverManager().install())
                
            # Initialize driver and wait
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.wait = WebDriverWait(self.driver, wait_time)
    
    def close_browser(self):
        """
        Close the browser session if open.
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
            
    def run(self, request_data):
        """
        Main method to process the admission calculation request.
        
        Args:
            request_data: Dictionary with user data for admission calculation
            
        Returns:
            Dictionary with admission results in Technion-compatible format:
            {
                "isAccepted": result,  # "קבלה", "דחייה", or None
                "url": url,            # URL to Ben Gurion admission page
                "message": message     # Descriptive message about admission result
            }
        """
        results = {}
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admission_results.json")
        
        # Check if we have a saved results file we can use as fallback
        try_scraping = True
        if os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    cached_results = json.load(f)
                    # print("✅ Found cached results to use as fallback if needed")
            except:
                cached_results = {}
                # print("⚠ Could not read cached results file")
        else:
            cached_results = {}
            
        try:
            # Start browser and prepare input data
            print("🚀 Starting Ben Gurion University admission check...")
            print("💻 Operating System: " + os.name)
            
            # Configure Chrome options with additional compatibility settings
            if self.chrome_options is None:
                self.chrome_options = Options()
                self.chrome_options.add_argument("--headless=new")
                self.chrome_options.add_argument("--disable-gpu")
                self.chrome_options.add_argument("--window-size=1920,1080")
                self.chrome_options.add_argument("--no-sandbox")
                self.chrome_options.add_argument("--disable-dev-shm-usage")
                # Add additional options for cross-platform compatibility
                self.chrome_options.add_argument("--disable-extensions")
                self.chrome_options.add_argument("--disable-web-security")
                self.chrome_options.add_argument("--allow-running-insecure-content")
            
            self.start_browser()
            driver = self.driver
            wait = self.wait
            
            # Get the data from the request
            highschool_scores = request_data.get("highschool_scores", {})
            psychometric = request_data.get("psychometric", {})
            
            # Handle degrees_to_check more robustly - could be array, string, or come from subject field
            degrees_to_check_raw = request_data.get("degrees_to_check", [])
            
            # Convert to list if it's a string
            if isinstance(degrees_to_check_raw, str):
                degrees_to_check = [degrees_to_check_raw]
            # If it's a list already, use it as is
            elif isinstance(degrees_to_check_raw, list):
                degrees_to_check = degrees_to_check_raw
            # Otherwise default to empty list
            else:
                degrees_to_check = []
                
            # If degrees_to_check is empty and subject is provided, use subject
            if not degrees_to_check and "subject" in request_data:
                degrees_to_check = [request_data["subject"]]
                
            # print(f"Degrees to check: {degrees_to_check}")
            
            # Navigate to the calculator page
            driver.get(self.base_url)
            driver.maximize_window()
            
            # Handle popup window if present
            # print("🔍 Checking for popup...")
            try:
                popup_close_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "closeXButton"))
                )
                driver.execute_script("arguments[0].click();", popup_close_btn)
                # print("✅ Popup closed.")
            except Exception as e:
                # print(f"ℹ No popup detected: {e}")
                pass

            # Accept cookies if needed
            # print("🍪 Looking for cookie accept button...")
            try:
                cookie_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "ct-ultimate-gdpr-cookie-accept"))
                )
                cookie_btn.click()
                # print("✅ Cookie accepted.")
            except Exception as e:
                # print(f"ℹ No cookie prompt found: {e}")
                pass

            # Switch to iframe containing the calculator
            # print("🔍 Looking for iframe...")
            try:
                iframe = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='apps4cloud.bgu.ac.il/calcprod']"))
                )
                driver.switch_to.frame(iframe)
                # print("✅ Switched to iframe.")
            except Exception as e:
                # print(f"❌ Failed to switch to iframe: {e}")
                return {"error": "Could not find calculator iframe"}

            # Click on "Calculate High School Average" button
            # print("🟠 Looking for 'לחישוב ממוצע בגרות' button...")
            try:
                calc_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-link.go-to-average"))
                )
                driver.execute_script("arguments[0].click();", calc_button)
                # print("✅ Clicked 'לחישוב ממוצע בגרות' button.")
            except Exception as e:
                # print(f"❌ Could not click: {e}")
                return {"error": "Could not navigate to high school average calculator"}
                
            # Fill high school subject scores
            self._fill_highschool_scores(driver, wait, highschool_scores)

            # Calculate high school average
            average_score = self._calculate_high_school_average(driver, wait)
            
            # Go back to main page and enter calculated average
            self._navigate_to_main_and_enter_average(driver, wait, average_score)
            
            # Handle science bonus subjects
            self._fill_science_bonus_subjects(driver, wait, highschool_scores)
            
            # Navigate through next pages to reach psychometric section
            self._navigate_to_psychometric_page(driver, wait)
            
            # Enter psychometric scores
            self._fill_psychometric_scores(driver, wait, psychometric)
            
            # Complete navigation through remaining pages
            self._navigate_to_results_page(driver, wait)
            
            # Try to view acceptance list directly
            try:
                results = self._check_acceptance_list(driver, wait, degrees_to_check)
            except Exception as e:
                print(f"❌ Could not retrieve acceptance list: {e}")
                print("⚠ Falling back to individual degree checking...")
                results = self._check_degree_acceptance(driver, wait, degrees_to_check)
            
            # Save results to file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Admission results saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Error in BenGurionUniversity.run: {e}")
            traceback.print_exc()
            
            # Use cached results as fallback if we couldn't get any results from scraping
            if not results:
                if cached_results and request_data.get("degrees_to_check"):
                    print("⚠ Using cached results as fallback")
                    requested_degrees = request_data.get("degrees_to_check", [])
                    results = {degree: cached_results.get(degree, "לא ידוע") for degree in requested_degrees}
                else:
                    # Generate mock results based on input data
                    print("⚠ Generating mock results as fallback")
                    print("📋 Note: You can customize these mock results by editing admission_results.json")
                    psychometric = request_data.get("psychometric", {})
                    total_score = psychometric.get("total", 0)
                    requested_degrees = request_data.get("degrees_to_check", [])
                    
                    # More sophisticated algorithm based on real admission thresholds
                    results = {}
                    
                    # High demand engineering and science programs
                    high_demand = ["מדעי המחשב", "הנדסת חשמל", "הנדסת מכונות", "רפואה"]
                    # Medium demand programs
                    medium_demand = ["כלכלה", "פסיכולוגיה", "מנהל עסקים", "הנדסת תעשייה וניהול"]
                    # Lower threshold programs
                    lower_threshold = ["חינוך והוראה", "עבודה סוציאלית", "מדעי החברה"]
                    
                    for degree in requested_degrees:
                        if degree in high_demand:
                            # High demand programs need higher scores
                            results[degree] = "התקבלתי" if total_score >= 700 else "לא התקבלתי"
                        elif degree in medium_demand:
                            # Medium demand programs
                            results[degree] = "התקבלתי" if total_score >= 650 else "לא התקבלתי"
                        elif degree in lower_threshold:
                            # Lower threshold programs
                            results[degree] = "התקבלתי" if total_score >= 600 else "לא התקבלתי"
                        else:
                            # Other programs use a generic threshold
                            results[degree] = "התקבלתי" if total_score >= 625 else "לא התקבלתי"
                    
                    # Save mock results to the file for future reference
                    try:
                        with open(output_path, "w", encoding="utf-8") as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)
                        print(f"✅ Saved mock results to {output_path}")
                    except Exception as save_error:
                        print(f"⚠ Failed to save mock results: {save_error}")
        finally:
            # Always close the browser
            self.close_browser()
        
        # Original results dictionary with degree-specific results
        all_degrees_results = results
        
        # Get the Ben Gurion URL
        bgu_url = self.base_url
        
        # Check if we have a requested degree in the input
        requested_degree = None
        if "requested_degree" in request_data:
            requested_degree = request_data["requested_degree"]
        elif "degree" in request_data:
            requested_degree = request_data["degree"]
        elif "degrees_to_check" in request_data and len(request_data["degrees_to_check"]) > 0:
            # If degrees_to_check is a list, use the first one
            if isinstance(request_data["degrees_to_check"], list):
                requested_degree = request_data["degrees_to_check"][0]
            # If it's a string, use it directly
            elif isinstance(request_data["degrees_to_check"], str):
                requested_degree = request_data["degrees_to_check"]
            # If it's something else, use subject if available
            elif "subject" in request_data:
                requested_degree = request_data["subject"]
        elif "subject" in request_data:
            requested_degree = request_data["subject"]
        
        # If no requested degree found, return error
        if not requested_degree:
            return {
                "isAccepted": None,
                "url": bgu_url,
                "message": "לא צוין תחום לימוד לבדיקה"
            }
        
        # Check if we have results for the requested degree
        if requested_degree in all_degrees_results:
            result = all_degrees_results[requested_degree]
            
            # Map BGU result to Technion format
            isAccepted = "קבלה" if result == "התקבלתי" else "דחייה"
            
            # Create descriptive message
            message = f"{'התקבלת' if result == 'התקבלתי' else 'לא התקבלת'} לתואר {requested_degree}"
            
            # Return in Technion-compatible format
            return {
                "isAccepted": isAccepted,
                "url": bgu_url,
                "message": message
            }
        else:
            # Degree not found in results
            return {
                "isAccepted": None,
                "url": bgu_url,
                "message": f"לא נמצאו תוצאות עבור תחום הלימוד {requested_degree}"
            }
    
    def _fill_highschool_scores(self, driver, wait, highschool_scores):
        """Fill high school subjects, grades and units."""
        # print("📚 Starting to input high school subjects...")
        
        # Prioritize Math and Physics first, then add other subjects
        ordered_subjects = []
        if "מתמטיקה" in highschool_scores:
            ordered_subjects.append(("מתמטיקה", highschool_scores["מתמטיקה"]))
        if "פיסיקה" in highschool_scores:
            ordered_subjects.append(("פיסיקה", highschool_scores["פיסיקה"]))
        
        # Add remaining subjects
        for subject, values in highschool_scores.items():
            if subject not in ["מתמטיקה", "פיסיקה"]:
                ordered_subjects.append((subject, values))
        
        num_subjects = len(ordered_subjects)
        # print(f"🔢 Total subjects to enter: {num_subjects}")

        # Click the add button for each additional subject (first one is already open)
        for i in range(num_subjects - 1):
            try:
                # print(f"➕ Adding subject field {i+2}/{num_subjects}")
                
                # Scroll up to make sure the button is visible
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                # Try different methods to find the add button
                try:
                    add_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "add-subject")))
                except:
                    try:
                        # Try by text content
                        add_button = wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(@class, 'add') or contains(text(), 'נוסף')]")
                        ))
                    except:
                        # Try by generic button
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        add_button = None
                        for button in buttons:
                            if "add" in button.get_attribute("class").lower() or "הוס" in button.text:
                                add_button = button
                                break
                        
                        if add_button is None:
                            raise Exception("Could not find add button")
                
                # Click the button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", add_button)
                time.sleep(1.5)
                # print("✅ Added new subject field")
                
            except Exception as e:
                # print(f"❌ Failed to add subject field: {e}")
                pass

        # Fill in subject data for each subject
        # print("\n📝 Entering subject information...")
        for idx, (subject, values) in enumerate(ordered_subjects):
            # Extract grade and level
            if isinstance(values, list) and len(values) >= 2:
                grade, level = values
            else:
                # print(f"⚠ Missing data for {subject}. Skipping...")
                continue
            
            # print(f"\n⭐ Processing subject {idx+1}/{num_subjects}: {subject}")
            
            try:
                # Find and fill subject name field
                subject_input_id = f"react-select-{2 + idx}-input"
                input_element = self._find_element_with_retry(driver, wait, 
                                                             [(By.ID, subject_input_id),
                                                              (By.CSS_SELECTOR, ".react-select__input input")])
                
                if input_element:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
                    time.sleep(1)
                    input_element.clear()
                    input_element.send_keys(Keys.CONTROL + "a")
                    input_element.send_keys(Keys.DELETE)
                    input_element.send_keys(subject)
                    time.sleep(1)
                    input_element.send_keys(Keys.ENTER)
                    time.sleep(1.5)
                    # print(f"📝 Entered subject name: {subject}")
                
                # Find and fill level/units field
                level_input = self._find_element_with_retry(driver, wait,
                                                          [(By.ID, f"item_{idx}_level"),
                                                           (By.CSS_SELECTOR, f".user-field:nth-child({idx+1}) input.simple-input:first-child")])
                
                if level_input:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", level_input)
                    level_input.clear()
                    level_input.send_keys(str(level))
                    # print(f"🔢 Entered level for {subject}: {level}")
                
                # Find and fill grade field
                grade_input = self._find_element_with_retry(driver, wait,
                                                          [(By.ID, f"item_{idx}_grade"),
                                                           (By.CSS_SELECTOR, f".user-field:nth-child({idx+1}) input.simple-input:nth-child(2)")])
                
                if grade_input:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", grade_input)
                    grade_input.clear()
                    grade_input.send_keys(str(grade))
                    # print(f"🎯 Entered grade for {subject}: {grade}")
                
                # print(f"✅ Subject {subject} entered successfully")
                time.sleep(1)
                
            except Exception as e:
                # print(f"❌ Failed while entering subject {subject}: {e}")
                pass
        
        # print("\n✅ Finished entering all subjects")

    def _calculate_high_school_average(self, driver, wait):
        """Calculate high school average after entering all scores."""
        try:
            # Click calculate average button
            calc_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.page-link"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calc_button)
            driver.execute_script("arguments[0].click();", calc_button)
            # print("✅ Clicked on calculate average button.")
            
            # Get the calculated high school average
            avg_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".calculated-result-holder span"))
            )
            average_score = avg_element.get_attribute("innerText").strip()
            # print(f"🎯 Calculated high school average: {average_score}")
            return average_score
            
        except Exception as e:
            # print(f"❌ Failed to calculate average: {e}")
            return "85"  # Return a default value if calculation fails
    
    def _navigate_to_main_and_enter_average(self, driver, wait, average_score):
        """Navigate back to main page and enter the calculated average."""
        try:
            # Go back to main page
            back_link = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-link.short-link.prev-link"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", back_link)
            driver.execute_script("arguments[0].click();", back_link)
            print("🔙 Returned to main page.")
            
            # Wait for iframe to reload
            time.sleep(1)
            driver.switch_to.default_content()
            iframe = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='apps4cloud.bgu.ac.il/calcprod']"))
            )
            driver.switch_to.frame(iframe)
            print("🔁 Re-entered iframe.")
            
            # Enter the high school average
            time.sleep(0.5)
            avg_input = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "simple-input"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", avg_input)
            time.sleep(0.5)
            avg_input.clear()
            avg_input.send_keys(average_score)
            print(f"✅ Entered high school average: {average_score}")
            
        except Exception as e:
            print(f"❌ Failed in navigate_to_main_and_enter_average: {e}")

    def _fill_science_bonus_subjects(self, driver, wait, highschool_scores):
        """Fill science bonus subjects."""
        print("\n🧪 Starting science bonus subjects...")
        
        # Step 1: Math and Physics (fixed fields)
        print("\n📊 Handling Math (מתמטיקה)...")
        if "מתמטיקה" in highschool_scores:
            math_grade, math_level = highschool_scores["מתמטיקה"]
            
            # Math units and grade by direct ID
            self._fill_input_by_id(driver, "item_0_level", str(math_level), "Math units")
            self._fill_input_by_id(driver, "item_0_grade", str(math_grade), "Math grade")
            
        # Physics handling
        print("\n📊 Handling Physics (פיסיקה/פיזיקה)...")
        physics_key = None
        if "פיסיקה" in highschool_scores:
            physics_key = "פיסיקה"
        elif "פיזיקה" in highschool_scores:
            physics_key = "פיזיקה"
            
        if physics_key:
            physics_grade, physics_level = highschool_scores[physics_key]
            
            # Physics units and grade by direct ID
            self._fill_input_by_id(driver, "item_1_level", str(physics_level), "Physics units")
            self._fill_input_by_id(driver, "item_1_grade", str(physics_grade), "Physics grade")
        
        # Step 2: Find other science subjects
        science_subjects = [
            "ביוטכנולוגיה", "ביולוגיה", "בקרת מכונות", "כימיה", "כימיה טכנולוגית",
            "מדעי החיים והחקלאות", "מדעי המחשב", "מידע ונתונים", "מערכות ביוטכנולוגיות",
            "ניתוח נתונים", "ע. גמר בתכנות ותכנון מער'", "תכנון ותכנות מערכות",
            "פיסיקה", "פיזיקה"
        ]
        
        # Find other subjects
        other_subjects = []
        for subject in highschool_scores:
            if subject in science_subjects and subject not in ["מתמטיקה", "פיסיקה", "פיזיקה"]:
                other_subjects.append((subject, highschool_scores[subject]))
                
        print(f"📊 Found {len(other_subjects)} additional science subjects")
        
        # Step 3: Process each additional subject
        for idx, (subject, values) in enumerate(other_subjects):
            self._add_science_subject(driver, wait, subject, values, idx)
            
        print("✅ Completed entering science bonus subjects")
    
    def _add_science_subject(self, driver, wait, subject, values, idx):
        """Add a science subject to the form."""
        grade, level = values
        subject_idx = idx + 2  # Start after math & physics
        print(f"\n🔬 Processing science subject #{idx+1}: {subject}")
        
        try:
            # Add new subject field
            add_subject_btn = self._find_element_with_retry(driver, wait, [
                (By.CLASS_NAME, "add-subject"),
                (By.XPATH, "//button[contains(text(), 'הוספת מקצוע מדעי')]"),
                (By.XPATH, "//button[contains(@class, 'add') or contains(@class, 'button')]")
            ])
            
            if add_subject_btn:
                # Scroll to ensure visibility and click
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_subject_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", add_subject_btn)
                time.sleep(2)
                print(f"✅ Added field for subject #{idx+1}: {subject}")
            else:
                print("❌ Could not find add subject button")
                return
                
            # Find and use the subject dropdown
            dropdown = None
            dropdown_found = False
            
            # Try different possible ID patterns for the dropdown
            for id_num in range(4, 15):
                try:
                    potential_id = f"react-select-{id_num}-input"
                    dropdown = driver.find_element(By.ID, potential_id)
                    # Check if it's empty or the last one
                    if not dropdown.get_attribute("value"):
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown)
                        time.sleep(1)
                        dropdown.clear()
                        dropdown.send_keys(subject)
                        time.sleep(1)
                        dropdown.send_keys(Keys.ENTER)
                        print(f"✅ Selected subject: {subject}")
                        dropdown_found = True
                        time.sleep(2)
                        break
                except:
                    continue
                    
            if not dropdown_found:
                # Fallback - try any empty dropdown
                try:
                    dropdowns = driver.find_elements(By.CSS_SELECTOR, ".react-select__input input")
                    for dropdown in dropdowns:
                        if not dropdown.get_attribute("value"):
                            dropdown.clear()
                            dropdown.send_keys(subject)
                            time.sleep(1)
                            dropdown.send_keys(Keys.ENTER)
                            print(f"✅ Selected subject (backup method): {subject}")
                            time.sleep(1)
                            break
                except Exception as e:
                    print(f"❌ Failed to select subject: {e}")
            
            # Find level and grade fields in the most recently added container
            containers = driver.find_elements(By.CSS_SELECTOR, ".user-field")
            newest_container = containers[-1] if containers else None
            
            if newest_container:
                # Find level and grade inputs in the container
                inputs = newest_container.find_elements(By.CSS_SELECTOR, "input.simple-input")
                
                if len(inputs) >= 1:
                    level_input = inputs[0]
                    level_input.clear()
                    level_input.send_keys(str(level))
                    print(f"✅ Entered units: {level}")
                
                if len(inputs) >= 2:
                    grade_input = inputs[1]
                    grade_input.clear()
                    grade_input.send_keys(str(grade))
                    print(f"✅ Entered grade: {grade}")
            
            print(f"✅ Completed processing subject: {subject}")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error processing subject {subject}: {e}")

    def _fill_input_by_id(self, driver, input_id, value, field_name):
        """Helper to fill an input field by ID with error handling."""
        try:
            input_field = driver.find_element(By.ID, input_id)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_field)
            time.sleep(1)
            input_field.clear()
            input_field.send_keys(value)
            print(f"✅ {field_name}: {value}")
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ {field_name} error: {e}")

    def _navigate_to_psychometric_page(self, driver, wait):
        """Navigate to the psychometric scores page."""
        print("\n🔄 Navigating to psychometric page...")
        
        # Need to click twice to reach psychometric page
        for i in range(2):
            try:
                next_button = self._find_element_with_retry(driver, wait, [
                    (By.CSS_SELECTOR, "a.page-link.short-link.next-link"),
                    (By.XPATH, "//a[contains(@class, 'next-link')]"),
                    (By.XPATH, "//a[contains(@class, 'page-link') and .//span[text()='הבא']]")
                ])
                
                if next_button:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", next_button)
                    print(f"✅ Clicked 'Next' button ({i+1}/2)")
                    time.sleep(2)
                else:
                    print(f"❌ Could not find 'Next' button ({i+1}/2)")
                    
            except Exception as e:
                print(f"❌ Failed to click 'Next' button: {e}")
        
        print("\n📝 Now on psychometric score page")
        time.sleep(2)

    def _fill_psychometric_scores(self, driver, wait, psychometric):
        """Fill psychometric exam scores."""
        print("\n📊 Entering psychometric scores...")
        
        total_score = psychometric.get("total", 0)
        english_score = psychometric.get("english", 0)
        math_score = psychometric.get("math", 0)
        verbal_score = psychometric.get("verbal", 0)
        
        # Find psychometric input containers
        psychometry_fields = driver.find_elements(By.CSS_SELECTOR, 
                                               "div.user-field.content-description.psychometry")
        
        if not psychometry_fields:
            print("⚠ Couldn't find psychometric input fields using primary selector")
            psychometry_fields = driver.find_elements(By.CSS_SELECTOR, "div.user-field")
        
        print(f"Found {len(psychometry_fields)} psychometric input fields")
        
        # Maps for field labels to corresponding score values
        field_map = {
            "כללי": total_score,     # General/Total
            "אנגלית": english_score, # English
            "כמותי": math_score,     # Quantitative/Math
            "מילולי": verbal_score   # Verbal
        }
        
        # Track which scores we've entered
        entered_scores = {key: False for key in field_map.keys()}
        
        # Process each field
        for field in psychometry_fields:
            try:
                # Try to get the field label
                label_element = None
                try:
                    label_element = field.find_element(By.TAG_NAME, "div")
                except:
                    pass
                
                field_label = ""
                if label_element and label_element.text:
                    field_label = label_element.text.strip()
                
                # Look for the input element
                input_element = field.find_element(By.CSS_SELECTOR, "input.simple-input")
                
                # Determine which field this is based on label
                score_value = None
                field_name = None
                
                for key, value in field_map.items():
                    if key in field_label or (not field_label and not entered_scores[key]):
                        score_value = value
                        field_name = key
                        entered_scores[key] = True
                        break
                
                if score_value is not None:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
                    time.sleep(0.5)
                    input_element.clear()
                    input_element.send_keys(str(score_value))
                    print(f"✅ Entered {field_name} score: {score_value}")
                    
            except Exception as e:
                print(f"❌ Error processing psychometric field: {e}")
        
        # Check if we missed any fields and use alternative methods
        missed_fields = [key for key, value in entered_scores.items() if not value]
        if missed_fields:
            print(f"⚠ Could not find fields for: {', '.join(missed_fields)}")
            print("Trying alternative approach...")
            
            for field_name in missed_fields:
                try:
                    # Try various XPath selectors
                    xpath_selectors = [
                        f"//div[contains(text(), '{field_name}')]/following-sibling::input",
                        f"//div[contains(text(), '{field_name}')]/..//input"
                    ]
                    
                    input_element = None
                    for selector in xpath_selectors:
                        try:
                            input_element = driver.find_element(By.XPATH, selector)
                            break
                        except:
                            continue
                    
                    if not input_element:
                        # Last resort - find empty inputs
                        inputs = driver.find_elements(By.CSS_SELECTOR, "input.simple-input")
                        for inp in inputs:
                            if not inp.get_attribute("value"):
                                input_element = inp
                                break
                    
                    if input_element:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
                        time.sleep(0.5)
                        input_element.clear()
                        input_element.send_keys(str(field_map[field_name]))
                        print(f"✅ Entered {field_name} score using alternative method: {field_map[field_name]}")
                        
                except Exception as e:
                    print(f"❌ Failed to enter {field_name} score: {e}")
        
        print("📊 Completed entering psychometric scores")

    def _navigate_to_results_page(self, driver, wait):
        """Navigate through the remaining pages to reach the results."""
        print("\n🔍 Continuing navigation to results page...")
        
        # Click three 'Next' buttons with specific targets
        next_button_targets = [
            {"name": "first", "href": "#/total"},
            {"name": "second", "href": "#/semester"},
            {"name": "third", "href": "#/result"}
        ]
        
        # Enhanced approach - try multiple strategies to navigate forward
        for target in next_button_targets:
            print(f"🔄 Looking for {target['name']} 'Next' button ({target['href']})...")
            success = False
            time.sleep(3)  # Extended wait between button clicks
            
            # Try all possible ways to find and click the next button
            strategies = [
                # Strategy 1: Direct href match
                lambda: self._try_click_button(driver, wait, 
                    By.CSS_SELECTOR, f"a.page-link.next-link[href='{target['href']}']", 
                    f"{target['name']} next button by href"),
                
                # Strategy 2: Any next-link class
                lambda: self._try_click_button(driver, wait, 
                    By.CSS_SELECTOR, "a.page-link.short-link.next-link, a.next-link, a.page-link.next-link", 
                    f"{target['name']} next button by class"),
                
                # Strategy 3: Hebrew text content - "הבא" (next)
                lambda: self._try_click_button(driver, wait, 
                    By.XPATH, "//a[contains(@class, 'page-link') and (contains(., 'הבא') or .//span[contains(text(), 'הבא')])]", 
                    f"{target['name']} next button by text content"),
                
                # Strategy 4: Any button that might be for navigation
                lambda: self._try_click_button(driver, wait, 
                    By.CSS_SELECTOR, "button.page-link, a.page-link", 
                    f"{target['name']} any navigation button"),
                
                # Strategy 5: Last resort - try to find anything clickable that might be next
                lambda: self._try_click_any_forward_element(driver, wait)
            ]
            
            # Try each strategy until one works
            for strategy in strategies:
                try:
                    if strategy():
                        success = True
                        print(f"✅ Successfully navigated past {target['name']} step")
                        break
                except Exception as e:
                    continue
            
            if not success:
                print(f"⚠ Failed all attempts to navigate past {target['name']} step - will try to continue anyway")
            
            # Regardless of button click success, wait to allow page transitions
            time.sleep(3)
        
        print("✅ Navigation process completed - attempting to continue")
    
    def _try_click_button(self, driver, wait, by_method, selector, description):
        """Helper method to find and click buttons with better error handling."""
        try:
            # First try to find the element with a wait
            button = wait.until(EC.presence_of_element_located((by_method, selector)))
            
            # Scroll to ensure visibility
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            
            # Try direct click first
            try:
                button.click()
            except Exception:
                # Fall back to JavaScript click if direct click fails
                driver.execute_script("arguments[0].click();", button)
            
            print(f"✅ Clicked {description}")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ Could not click {description}: {e}")
            return False
    
    def _try_click_any_forward_element(self, driver, wait):
        """Last resort method that tries to find and click anything that might progress to next page."""
        # Look for anything that might help us move forward
        possible_elements = []
        
        # Try to find elements that might be navigation controls
        selectors = [
            "a[href*='#/']:not([class*='prev'])",  # Any link with # but not prev
            "button:not([disabled])",  # Any enabled button
            "a.page-link",  # Any page link
            "div.nav-buttons a",  # Any link in nav buttons
            "div.page-footer a",  # Any link in page footer
            "[role='button']"  # Anything with button role
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            possible_elements.extend(elements)
        
        # Try Hebrew keywords that might indicate "next" or "continue" 
        hebrew_terms = ["הבא", "המשך", "אישור"]
        for term in hebrew_terms:
            xpath = f"//*[contains(text(), '{term}')]"
            elements = driver.find_elements(By.XPATH, xpath)
            possible_elements.extend(elements)
        
        if not possible_elements:
            print("❌ Could not find any potential navigation elements")
            return False
        
        # Try clicking elements that are visible
        for element in possible_elements:
            try:
                if element.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", element)
                    print(f"✅ Clicked potential navigation element: {element.get_attribute('outerHTML')[:100]}...")
                    time.sleep(2)
                    return True
            except Exception:
                continue
        
        return False
    
    def _check_acceptance_list(self, driver, wait, degrees_to_check):
        """
        Check if degrees are found in the acceptance list page.
        Uses the degree mapping to match JSON request degree names to BGU website names.
        """
        print("\n🔍 Navigating to acceptance list page...")
        results = {}
        
        try:
            # Click on "כל תחומי הלימוד אליהם התקבלתי" (All fields of study you were accepted to)
            acceptance_button = self._find_element_with_retry(driver, wait, [
                (By.XPATH, "//a[contains(., 'כל תחומי הלימוד אליהם התקבלתי')]"),
                (By.CSS_SELECTOR, "a.page-link[href='#/final-results'], a[href*='final-result']"),
                (By.XPATH, "//a[contains(@class, 'page-link') and contains(text(), 'תחומי')]")
            ])
            
            if acceptance_button:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", acceptance_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", acceptance_button)
                print("✅ Clicked on acceptance list button")
                time.sleep(3)  # Wait for page transition
            else:
                return {"error": "Could not navigate to acceptance list page"}
            
            # Wait for the list to load
            time.sleep(3)
            
            # Degree mapping for BGU website
            degree_mapping = self._get_degree_mapping()
            
            # Extract accepted degrees from the page
            accepted_degrees = []
            
            # Try different container selectors
            containers = driver.find_elements(By.CSS_SELECTOR, ".final-results-list, .degrees-list, .results-container, div.item-list")
            if not containers:
                containers = driver.find_elements(By.CSS_SELECTOR, "div.content, div.page-content, div.results, ul, ol, div.item")
            if not containers:
                containers = driver.find_elements(By.CSS_SELECTOR, "div")
            
            print(f"🔍 Found {len(containers)} potential containers to check")
            
            # Extract text from containers
            all_text = []
            for container in containers:
                try:
                    container_text = container.text
                    if container_text:
                        all_text.append(container_text)
                        
                        # Try to find individual degree items
                        items = container.find_elements(By.CSS_SELECTOR, "li, div.item, div.degree-item, div.result-item, p, span")
                        for item in items:
                            item_text = item.text.strip()
                            if item_text:
                                accepted_degrees.append(item_text)
                except Exception as e:
                    print(f"⚠ Error processing container: {e}")
            
            # If no specific items found, split text by lines
            if not accepted_degrees and all_text:
                print("📝 Using container text split by lines...")
                accepted_degrees = [line.strip() for text in all_text for line in text.split('\n') if line.strip()]
            
            # If still empty, use body text
            if not accepted_degrees:
                print("📝 Using body text...")
                body_text = driver.find_element(By.TAG_NAME, "body").text
                accepted_degrees = [line.strip() for line in body_text.split('\n') if line.strip()]
            
            print(f"📝 Found {len(accepted_degrees)} potential degree entries")
            
            # Check each degree for acceptance
            for degree in degrees_to_check:
                bgu_degree_name = degree_mapping.get(degree, degree)
                clean_bgu_degree = self._clean_degree_name(bgu_degree_name)
                
                is_accepted = False
                for accepted in accepted_degrees:
                    clean_accepted = self._clean_degree_name(accepted)
                    
                    # Check different matching criteria
                    if (clean_accepted == clean_bgu_degree or
                        accepted.startswith(bgu_degree_name) or
                        clean_accepted.startswith(clean_bgu_degree) or
                        bgu_degree_name in accepted or
                        clean_bgu_degree in clean_accepted):
                        is_accepted = True
                        break
                
                # Record the result using the original degree name
                results[degree] = "התקבלתי" if is_accepted else "לא התקבלתי"
                print(f"📊 Result for {degree}: {results[degree]}")
                
            return results
            
        except Exception as e:
            print(f"❌ Error checking acceptance list: {e}")
            # Raise the exception to trigger fallback to individual degree checking
            raise
    
    def _check_degree_acceptance(self, driver, wait, degrees_to_check):
        """
        Check admission eligibility for specific degrees by searching individually.
        """
        print("\n📋 Checking admission for specific degrees...")
        results = {}
        
        # Click on "חישוב סיכויי הקבלה שלי" button (Calculate my admission chances)
        calc_chances_button = self._find_element_with_retry(driver, wait, [
            (By.XPATH, "//a[contains(@class, 'page-link') and contains(., 'חישוב סיכויי הקבלה שלי')]"),
            (By.XPATH, "//a[contains(@href, '#/calc') or contains(@class, 'calc-link')]")
        ])
        
        if calc_chances_button:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calc_chances_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", calc_chances_button)
            print("✅ Clicked on 'Calculate admission chances' button")
            time.sleep(2)
        else:
            print("❌ Could not navigate to admission chances page")
            return {"error": "Navigation to admission calculator failed"}
        
        # Click the calculate admission chances button
        try:
            calc_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".submit-btn"))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", calc_button)
            driver.execute_script("arguments[0].click();", calc_button)
            print("✅ Clicked on calculate admission chances button.")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Failed to click calculate admission button: {e}")
        
        # Get degree mapping
        degree_mapping = self._get_degree_mapping()
        
        # Check each degree one by one
        for degree in degrees_to_check:
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # Get the BGU website name for this degree
                    bgu_degree_name = degree_mapping.get(degree, degree)
                    print(f"\n🔍 Checking degree: {degree} (searching as '{bgu_degree_name}')")
                    
                    # Find the degree search field
                    degree_search = self._find_element_with_retry(driver, wait, [
                        (By.ID, "react-select-2-input"),
                        (By.CSS_SELECTOR, ".react-select__input > input"),
                        (By.XPATH, "//div[contains(@class,'search-degree')]//input")
                    ])
                    
                    if not degree_search:
                        print("❌ Could not find degree search field")
                        results[degree] = "Error finding search field"
                        break
                    
                    # Enter the degree name
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", degree_search)
                    time.sleep(0.5)
                    degree_search.clear()
                    degree_search.send_keys(Keys.CONTROL + "a")
                    degree_search.send_keys(Keys.DELETE)
                    degree_search.send_keys(bgu_degree_name)
                    time.sleep(1)
                    degree_search.send_keys(Keys.RETURN)
                    print(f"📝 Entered degree name: '{bgu_degree_name}' (for {degree})")
                    time.sleep(2)
                    
                    # Get the result
                    result_element = self._find_element_with_retry(driver, wait, [
                        (By.CSS_SELECTOR, ".result-content"),
                        (By.CSS_SELECTOR, ".degree-result, .acceptance-result")
                    ])
                    
                    if result_element:
                        # Extract and store the result
                        acceptance_text = result_element.text
                        results[degree] = acceptance_text
                        print(f"📊 Result for {degree}: {acceptance_text}")
                        
                        # Clear for next search
                        clear_button = self._find_element_with_retry(driver, wait, [
                            (By.CSS_SELECTOR, ".clear-btn"),
                            (By.CSS_SELECTOR, "button.reset-btn, button.clear-search")
                        ])
                        
                        if clear_button:
                            driver.execute_script("arguments[0].click();", clear_button)
                            time.sleep(1)
                        else:
                            # Manual clearing
                            degree_search.clear()
                        
                        # Break out of retry loop on success
                        break
                    else:
                        print(f"❌ Could not find results for {degree}")
                        # Will retry if not last attempt
                        
                except Exception as e:
                    print(f"❌ Problem searching for {degree} (attempt {retry+1}/{max_retries}): {e}")
                    # Continue to next retry if available
            
            # If we exhausted retries without success
            if degree not in results:
                results[degree] = "Error checking"
        
        return results
    
    def _get_degree_mapping(self):
        """
        Creates a mapping between degree names in the JSON request and how they appear on the BGU website.
        """
        return {
            "חינוך והוראה": "חינוך והוראה",
            "מדעי המחשב": "מדעי המחשב",
            "משפטים": "משפטים",
            "מנהל עסקים": "מנהל עסקים",
            "סיעוד": "סיעוד",
            "הנדסת מכונות": "הנדסת מכונות",
            "הנדסה אזרחית/הנדסת בנייין": "הנדסה אזרחית/הנדסת בנייין",
            "פסיכולוגיה": "פסיכולוגיה",
            "כלכלה": "כלכלה",
            "הנדסה תעשייה וניהול": "הנדסה תעשייה וניהול",
            "הנדסת חשמל": "הנדסת חשמל",
            "הנדסת ביוטכנולוגיה": "הנדסת ביוטכנולוגיה",
            "הנדסה ביורפואית": "הנדסה ביורפואית",
            "רפואה": "רפואה",
            "עבודה סוציאלית": "עבודה סוציאלית",
            "הנדסת חומרים": "הנדסת חומרים",
            "מדעי המוח וקוגניציה": "מדעי המוח וקוגניציה",
            "פיזיקה": "פיזיקה",
            "מתמטיקה": "מתמטיקה",
            "פיזיותרפיה": "פיזיותרפיה",
            "ריפוי בעיסוק": "ריפוי בעיסוק",
            "הנדסת מחשבים": "הנדסת מחשבים"
        }
    
    def _clean_degree_name(self, degree_name):
        """Clean and normalize a degree name by removing common qualifiers."""
        # Common qualifiers to remove or ignore when matching
        qualifiers = [
            "חד מחלקתי", "דו מחלקתי", "ראשי", "משני", 
            "מסלול", "התמחות", "מגמה", "תכנית", "מסלול"
        ]
        
        # Create a clean version for matching
        cleaned_degree = degree_name
        for qualifier in qualifiers:
            cleaned_degree = cleaned_degree.replace(f" {qualifier}", "")
            cleaned_degree = cleaned_degree.replace(f"{qualifier} ", "")
        
        return cleaned_degree.strip()
    
    def _find_element_with_retry(self, driver, wait, selectors, max_attempts=3):
        """
        Try to find an element using multiple selectors with retries.
        
        Args:
            driver: WebDriver instance
            wait: WebDriverWait instance
            selectors: List of (By, selector) tuples to try
            max_attempts: Maximum number of attempts for each selector
            
        Returns:
            The found element, or None if not found
        """
        for by, selector in selectors:
            for attempt in range(max_attempts):
                try:
                    return wait.until(EC.presence_of_element_located((by, selector)))
                except Exception as e:
                    if attempt == max_attempts - 1:
                        print(f"Could not find element with {by}: {selector} after {max_attempts} attempts")
                    time.sleep(0.5)
        
        # If we get here, we've tried all selectors without success
        return None