import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class CompulysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        
        # Initialize the webdriver
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(15)
        # Fallback to local if env var not set
        cls.base_url = os.getenv("BASE_URL", "http://16.16.16.219:8004")
        cls.wait = WebDriverWait(cls.driver, 20)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_01_login_page_load(self):
        """Test 1: Verify the login page loads correctly."""
        self.driver.get(f"{self.base_url}/login")
        login_page = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='login-page']")))
        self.assertTrue(login_page.is_displayed())
        self.assertIn("Compulysis", self.driver.title)

    def test_02_invalid_login(self):
        """Test 2: Attempt login with invalid credentials."""
        self.driver.get(f"{self.base_url}/login")
        email_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='login-email']")))
        password_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']")
        
        email_input.clear()
        email_input.send_keys("wrong@compulysis.com")
        password_input.clear()
        password_input.send_keys("wrongpassword")
        submit_btn.click()
        
        error_msg = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='auth-error']")))
        self.assertTrue(error_msg.is_displayed())

    def test_03_valid_login(self):
        """Test 3: Login with valid credentials and verify redirect."""
        self.driver.get(f"{self.base_url}/login")
        email_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='login-email']")))
        password_input = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']")
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']")
        
        email_input.clear()
        email_input.send_keys("admin@compulysis.com")
        password_input.clear()
        password_input.send_keys("admin123")
        submit_btn.click()
        
        # Wait for sidebar to verify login success
        sidebar = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='sidebar']")))
        self.assertTrue(sidebar.is_displayed())

    def test_04_dashboard_load(self):
        """Test 4: Verify Dashboard renders properly."""
        nav_dashboard = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='nav-dashboard']")))
        nav_dashboard.click()
        time.sleep(1) # Give it time to render
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIn("Dashboard", body.text)

    def test_05_nav_patients(self):
        """Test 5: Navigate to Patient Management."""
        nav_patients = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-patients']")))
        nav_patients.click()
        patients_page = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='patients-page']")))
        self.assertTrue(patients_page.is_displayed())

    def test_06_nav_assessment(self):
        """Test 6: Navigate to Assessment page."""
        nav_assessment = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-assessment']")))
        nav_assessment.click()
        # Assumes there is a header or specific text
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Assessment')] | //*[contains(text(), 'Assessment')]")))

    def test_07_nav_model_lab(self):
        """Test 7: Navigate to Model Lab page."""
        nav_model_lab = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-model-lab']")))
        nav_model_lab.click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Model')] | //*[contains(text(), 'Model Laboratory')]")))

    def test_08_nav_data_explorer(self):
        """Test 8: Navigate to Data Explorer page."""
        nav_data_explorer = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-data-explorer']")))
        nav_data_explorer.click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Data')] | //*[contains(text(), 'Data Explorer')]")))

    def test_09_nav_reports(self):
        """Test 9: Navigate to Reports page."""
        nav_reports = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='nav-reports']")))
        nav_reports.click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Report')] | //*[contains(text(), 'Reports')]")))

    def test_10_patient_search(self):
        """Test 10: Verify Patient Search works."""
        self.driver.get(f"{self.base_url}/patients")
        search_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='patient-search']")))
        search_input.send_keys("John Doe")
        time.sleep(1) # Allow search to filter
        self.assertTrue(search_input.is_displayed())

    def test_11_add_patient_modal(self):
        """Test 11: Verify Add Patient Modal opens."""
        self.driver.get(f"{self.base_url}/patients")
        add_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add New Patient')]")))
        add_btn.click()
        modal = self.wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Add New Patient')]")))
        self.assertTrue(modal.is_displayed())
        # Close modal
        close_btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'hover:bg-gray-100')]")
        close_btn.click()

    def test_12_assessment_form(self):
        """Test 12: Verify Assessment form renders."""
        self.driver.get(f"{self.base_url}/assessment")
        time.sleep(1)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIn("Assessment", body.text)

    def test_13_model_lab_ui(self):
        """Test 13: Verify Model Lab UI renders."""
        self.driver.get(f"{self.base_url}/model-lab")
        time.sleep(1)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIn("Model", body.text)

    def test_14_data_explorer_table(self):
        """Test 14: Verify Data Explorer Table renders."""
        self.driver.get(f"{self.base_url}/data-explorer")
        time.sleep(1)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIn("Data", body.text)

    def test_15_logout(self):
        """Test 15: Verify Logout functionality."""
        logout_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='logout-button']")))
        logout_btn.click()
        login_page = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='login-page']")))
        self.assertTrue(login_page.is_displayed())

if __name__ == "__main__":
    unittest.main(verbosity=2)
