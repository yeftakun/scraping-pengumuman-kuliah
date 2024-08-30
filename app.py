import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

# Mengambil variabel dari .env
NIM = os.getenv('NIM')
PASSWORD = os.getenv('PASSWORD')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TELEGRAM_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
JSON_FILE = 'announcements.json'
MAX = int(os.getenv('MAX'))

# Path ke chromedriver
driver_service = Service('chromedriver.exe')  # Ganti dengan path yang benar
options = Options()
options.headless = True  # Set ke True untuk mode headless

# Inisialisasi WebDriver
driver = webdriver.Chrome(service=driver_service, options=options)

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

try:
    # Buka halaman login
    driver.get('https://inspire.unsrat.ac.id/')

    # Mengisi username dan password
    print("Input username dan password...")
    driver.find_element(By.NAME, 'username').send_keys(NIM)
    driver.find_element(By.NAME, 'password').send_keys(PASSWORD)

    # Klik tombol login
    login_button = driver.find_element(By.CSS_SELECTOR, '.btn.btn-danger.btn-round.btn-lg.btn-block')
    login_button.click()

    print("Mengakses halaman pengumuman...")
    driver.get('https://inspire.unsrat.ac.id/pengumuman/pengumuman/list')

    # Tunggu hingga navigasi selesai dan halaman pengumuman tersedia
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.product-info'))
    )

    # Tunggu hingga elemen dengan kelas 'product-info' tersedia
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
        # Ambil elemen <a> dan URL-nya
        link_element = announcement.find_element(By.CSS_SELECTOR, 'a.product-title')
        url = link_element.get_attribute('href')
        
        # Ambil judul pengumuman
        title_element = link_element.find_element(By.CSS_SELECTOR, 'h4')
        title = title_element.text if title_element else 'No title'
        
        # Ambil waktu pengumuman
        time_element = announcement.find_element(By.CSS_SELECTOR, 'span.badge-info')
        time = time_element.text if time_element else 'No time'
        
        # Ambil deskripsi pengumuman
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
    # Menutup browser
    driver.quit()
