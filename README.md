# Scraping Pengumuman Kuliah

### Setup

**Install modul**
```
pip install selenium requests python-dotenv webdriver-manager
```

**Driver**

**Chrome (windows)**

Download sesuai dengan versi chrome [disini](https://developer.chrome.com/docs/chromedriver/downloads) untuk chrome versi 115 keatas [disini](https://googlechromelabs.github.io/chrome-for-testing/), ekstrak dan taruh file exe di direktori utama.

**Firefox (Termux)**

```
pkg install geckodriver
pkg install which
which geckodriver
```
Copy path geckodriver dan taruh di `app2.py`

```
pkg install x11-repo
pkg install firefox
```

**Bot telegram**

Buat bot telegram [di sini](https://t.me/BotFather) dan salin bot token. Kirim pesan apapun di bot baru anda agar bot dapat mengirim pesan ke chat_id anda.

**Konfigurasi env**

Update nilai variabel pada file [.env-temp](.env-temp), lalu rename file menjadi `.env`. Untuk `CHAT_ID` anda bisa didapat dari [bot telegram ini](https://t.me/chatIDrobot).

---

### Run

```
python app.py
```

Untuk file `access2.py` terdapat looping dengan interval (tidak disarankan)
