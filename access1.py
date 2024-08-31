from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

# Load environment variables NIM and password
load_dotenv()
NIM = os.getenv("NIM")
PASSWORD = os.getenv("PASS")

first_run = True
reload = True

# Configure options
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)

# Open the login page
login_url = "https://inspire.unsrat.ac.id"
redirect_url = "https://inspire.unsrat.ac.id/pengumuman/pengumuman/list"
driver.get(login_url)

# Fill in the login form
username_field = driver.find_element(By.NAME, "username")
password_field = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
print('Memasukan username dan password')
username_field.send_keys(NIM)
password_field.send_keys(PASSWORD)
print('Login...')
login_button.click()

print('Mengakses halaman pengumuman')
driver.get(redirect_url)

# Wait for redirection to the desired page
try:
    WebDriverWait(driver, 10).until(EC.url_to_be(redirect_url))
    print("Berhasil ke halaman pengumuman '" + driver.current_url + "'")
except Exception as e:
    print("Gagal ke pengumuman. Halaman saat ini '" + driver.current_url + "'")
    print('Cek kembali username dan password - Menghentikan program...')


driver.quit()