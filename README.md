 🚗  Car Rental Management System

**Car Rental** is a GUI-based **Car Rental Management System** built with **Python + PyQt5 + SQLite**.  
It is lightweight yet complete, designed to help individuals or small car rental companies manage vehicles, customers, rental orders, and fines efficiently.

---

## ✨ Features

- **Vehicle Management**
  - Add / Edit / Delete vehicle records
  - Insurance expiry reminder (overdue: flashing red / within 3 days: yellow warning)
  - Column sorting (plate number, year, model)
  - Pagination & search by plate/model
  - Export vehicle list to CSV

- **Customer Management**
  - Add / Edit / Delete customer records
  - Unique phone number validation
  - Customer types: Normal, VIP, Blacklist
  - Double-click customer to view historical orders
  - Column sorting by name / phone / status
  - Export customer list to CSV

- **Order Management**
  - Add / Edit / Delete rental orders
  - Order renewal (extend end date)
  - Expiry reminders: 
    - 3 days before expiry → yellow highlight  
    - Expired ongoing/overdue orders → flashing red
  - Manage order status: ongoing/completed/overdue/cancelled
  - Pagination, searching by customer/vehicle/status
  - Export orders to CSV

- **Fine Management**
  - Add / Edit / Delete fine records
  - Paid / Unpaid distinction (unpaid highlighted red)
  - Local fine records + official Dubai Police fine query (via WebEngine)
  - Export fines to CSV

- **Languages**
  - 🌐 Multi-language support: **Chinese / English**
  - Automatically remembers your last selected language

- **Database**
  - Uses **SQLite (rental.db)** as backend, safe & stable
  - First run automatically migrates existing JSON data → SQLite
  - Easy backup and restore (just copy `rental.db`)

- **Modern UI**
  - Flat, clean, modern interface
  - Includes a custom icon (Ezown Car Rental Logo)
  - Can be bundled into a standalone `.exe` application

### 1. Requirements
- Python 3.8+  
- Recommended: use a virtual environment  
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Run
```bash
python MAIN.py
```

On first run, the system initializes `rental.db`.  
If legacy JSON files exist (`vehicle_data.json`, etc.), they will be automatically migrated into SQLite.

### 3. Build into an executable (Windows example)
A `build.bat` is included for one-click packaging, or manually run:

```bash
pyinstaller --noconsole --onefile --icon=ezown.ico --add-data "rental.db;." MAIN.py
```

The executable will be generated in the `dist/` folder.

---

## 📦 Project Structure

```
your_project/
├─ MAIN.py             # Main entry
├─ data.py             # Data access (SQLite + JSON migration)
├─ vehicle_page.py     # Vehicle Management
├─ customer_page.py    # Customer Management
├─ order_page.py       # Order Management
├─ fine_page.py        # Fine Management
├─ i18n.py             # Internationalization (multi-language)
├─ rental.db           # SQLite database file
├─ build.bat           # One-click build script
├─ requirements.txt    # Python dependencies
└─ README.md           # This file
```

---

## 📖 Tech Stack

- **Language**: Python 3.8+  
- **Framework**: PyQt5  
- **Database**: SQLite3  
- **Utilities**: JSON, CSV, shutil, datetime, sqlite3 standard lib  
- **Optional**: PyQtWebEngine (for Dubai Police fine query)

---

## ❤️ About

Developed by **Ezown Car Rental**,  
aiming to provide a simple but complete car rental management software suitable for small rental businesses.  

---

## 🙏 Thanks to

- PyQt5 & Qt Documentation  
- SQLite Official Documentation  
- GitHub Open Source Community  

---

👉 要不要我帮你再写一个 **requirements.txt** 内容（比如 `PyQt5`, `pytz`, `pyinstaller`, `PyQtWebEngine`），省得别人手动找依赖？
