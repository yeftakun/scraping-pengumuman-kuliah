from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv
import json
import requests
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

# Load environment variables NIM and password
load_dotenv()

NIM = os.getenv('NIM')
PASSWORD = os.getenv('PASS')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TELEGRAM_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
JSON_FILE = 'announcements.json'
MAX = int(os.getenv('MAX'))

first_run = True
reload = True

options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/91.0 Safari/537.36")

service = Service('/data/data/com.termux/files/usr/bin/geckodriver')  # pastikan geckodriver ada di PATH
driver = webdriver.Firefox(service=service, options=options)


def read_announcements():
    """Membaca pengumuman dari file JSON."""
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("File JSON tidak valid. Mengembalikan daftar kosong.")
            return []
    return []

def write_announcements(announcements):
    """Menulis pengumuman ke file JSON."""
    with open(JSON_FILE, 'w') as file:
        json.dump(announcements, file, indent=4)

def get_next_id(announcements):
    """Mengambil ID berikutnya untuk pengumuman baru."""
    if announcements:
        return max(ann['id'] for ann in announcements) + 1
    return 1

def check_and_clean_data(announcements):
    """Memeriksa jumlah data dan membersihkan jika mencapai 50."""
    if len(announcements) >= MAX:
        print("Jumlah pengumuman mencapai 50, menghapus semua data.")
        return []  # Menghapus semua data jika sudah mencapai 50
    return announcements

# Open the login page
login_url = "https://inspire.unsrat.ac.id"
redirect_url = "https://inspire.unsrat.ac.id/pengumuman/pengumuman/list"

try:
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

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.product-info'))
    )

    WebDriverWait(driver, 60).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product-info'))
    )

    # Ambil data pengumuman
    print("Mengambil data pengumuman...")
    announcements = driver.find_elements(By.CSS_SELECTOR, '.product-info')

    # Membaca pengumuman yang sudah ada dari file JSON
    existing_announcements = read_announcements()
    existing_announcements = check_and_clean_data(existing_announcements)  # Memeriksa dan membersihkan data jika perlu
    existing_urls = {ann['url'] for ann in existing_announcements}
    
    new_announcements = []
    next_id = get_next_id(existing_announcements)
    
    for announcement in announcements:
        # Ambil url dari <a>
        link_element = announcement.find_element(By.CSS_SELECTOR, 'a.product-title')
        url = link_element.get_attribute('href')
        
        # Ambil judul
        title_element = link_element.find_element(By.CSS_SELECTOR, 'h4')
        title = title_element.text if title_element else 'No title'
        
        # Ambil waktu
        time_element = announcement.find_element(By.CSS_SELECTOR, 'span.badge-info')
        time = time_element.text if time_element else 'No time'
        
        # Ambil deskripsi
        description_element = announcement.find_element(By.CSS_SELECTOR, 'span.product-description')
        description = description_element.text.strip() if description_element else 'No description'
        
        # Cek apakah URL pengumuman sudah ada
        if url not in existing_urls:
            # Tambah ID otomatis dan simpan pengumuman baru
            new_announcements.append({
                'id': next_id,
                'title': title,
                'time': time,
                'description': description,
                'url': url
            })
            next_id += 1
    
    # Menambahkan pengumuman baru ke file JSON
    if new_announcements:
        write_announcements(existing_announcements + new_announcements)
        
        # Format pesan untuk Telegram
        message = "PENGUMUMAN BARU:\n\n"
        for ann in new_announcements:
            message += f"{ann['title']}\n"
            message += f"Waktu: {ann['time']}\n"
            message += f"Deskripsi: {ann['description']}\n"
            message += f"URL: {ann['url']}\n-----------\n"

        # Kirimkan pesan ke Telegram
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
        }
        response = requests.post(TELEGRAM_URL, data=payload)
        
        if response.status_code == 200:
            print("Pesan berhasil dikirim ke Telegram.")
        else:
            print(f"Terjadi kesalahan saat mengirim pesan: {response.status_code}")
    else:
        print("Tidak ada pengumuman baru.")
finally:
    driver.quit()




# Wait for redirection to the desired page
# try:
#     WebDriverWait(driver, 10).until(EC.url_to_be(redirect_url))
#     print("Berhasil ke halaman pengumuman '" + driver.current_url + "'")
# except Exception as e:
#     print("Gagal ke pengumuman. Halaman saat ini '" + driver.current_url + "'")
#     print('Cek kembali username dan password - Menghentikan program...')


# driver.quit()
