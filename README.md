# C0rps3 — The Intelligence Tool

An interactive, modular **Open Source Intelligence (OSINT) REPL** framework built in Python for reconnaissance, footprinting, identity investigation, and infrastructure mapping.

---

## ⚡ Key Features

* **Interactive REPL Environment:** Clean command-line interface with persistent session handling and input parsing.
* **Network & Infrastructure Reconnaissance:**
  * **Shodan Integration:** Query host banners, exposed services, and known vulnerabilities.
  * **DNS Records:** Query `A`, `AAAA`, `MX`, `NS`, and `TXT` records.
  * **WHOIS & IP Geolocation:** Perform RDAP lookups and trace IP origin (city, country, ISP).
* **Identity & People OSINT:**
  * **Username Hunting:** Multi-platform username enumeration.
  * **Breach Intelligence:** Check email accounts against HaveIBeenPwned breach databases.
  * **Phone Intelligence:** Parse, validate, and extract carrier/regional metadata from phone numbers.
* **Web & Media Analysis:**
  * **EXIF Extraction:** Pull metadata, device info, and GPS coordinates from images.
  * **Web Recon:** Inspect HTTP headers and perform fast link/metadata web scraping.
  * **Paste Search:** Search public paste sites for leaked intelligence.
* **Social & Deep Lookups:**
  * **Twitter/X Lookup:** Query user profile data via API.
  * **Reverse Geocoding:** Convert raw coordinates `(lat, lon)` into addresses.
  * **Aggregated OSINT (`deep`):** Cross-correlate multiple intelligence modules across IP, domain, username, email, or phone targets.

---

## 📋 Available Commands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `help` | `help` | Display the interactive command list |
| `clear` | `clear` | Clear terminal screen |
| `about` | `about` | View tool version, mode, and configuration info |
| `shodan` | `shodan host <ip>`<br>`shodan search <query>` | Query Shodan for host intelligence and vulnerabilities |
| `dns` | `dns <domain>` | Retrieve domain DNS records (A/AAAA/MX/NS/TXT) |
| `whois` | `whois <target>` | Perform RDAP / WHOIS lookups for domains or IP addresses |
| `geo` | `geo <ip>` | Lookup IP geolocation, ISP, and organization data |
| `user` | `user <username>` | Enumerate usernames across web platforms |
| `email` | `email <addr>` | Perform HaveIBeenPwned breach lookups |
| `phone` | `phone <number>` | Parse phone numbers for carrier, region, and validity |
| `exif` | `exif <image_path>` | Extract EXIF metadata and geolocation from images |
| `headers`| `headers <url>` | Inspect HTTP/HTTPS response headers |
| `scrape` | `scrape <url>` | Extract page title, meta tags, and outbound links |
| `paste` | `paste <query>` | Search public paste sites for keywords/indicators |
| `twitter`| `twitter <handle>` | Lookup Twitter/X user profile data |
| `reverse`| `reverse <lat,lon>`| Reverse-geocode latitude and longitude coordinates |
| `deep` | `deep <type> <target>` | Run aggregated multi-module lookups (`ip`, `domain`, `user`, `email`, `phone`) |
| `exit` / `quit` | `exit` | Terminate the REPL session |

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.9+
* Active API keys for extended features (e.g., Shodan, Twitter Bearer Token, HaveIBeenPwned)

### 1. Clone the Repository
```bash
git clone [https://github.com/alpharomanticlesscharacterlessdelta/C0rps3.git](https://github.com/alpharomanticlesscharacterlessdelta/C0rps3.git)
cd C0rps3/C0rps3
'''
### 2. Install the 
