🚗Car Rental Management System
Car Rental is a GUI-based Car Rental Management System built with Python + PyQt5 + SQLite.
It is lightweight yet complete, designed to help individuals or small car rental companies manage vehicles, customers, rental orders, and fines efficiently.

✨ Features
Vehicle Management

Add / Edit / Delete vehicle records
Insurance expiry reminder (overdue: flashing red / within 3 days: yellow warning)
Column sorting (plate number, year, model)
Pagination & search by plate/model
Export vehicle list to CSV
Customer Management

Add / Edit / Delete customer records
Unique phone number validation
Customer types: Normal, VIP, Blacklist
Double-click customer to view historical orders
Column sorting by name / phone / status
Export customer list to CSV
Order Management

Add / Edit / Delete rental orders
Order renewal (extend end date)
Expiry reminders:
3 days before expiry → yellow highlight
Expired ongoing/overdue orders → flashing red
Manage order status: ongoing/completed/overdue/cancelled
Pagination, searching by customer/vehicle/status
Export orders to CSV
Fine Management

Add / Edit / Delete fine records
Paid / Unpaid distinction (unpaid highlighted red)
Local fine records + official Dubai Police fine query (via WebEngine)
Export fines to CSV
Languages

🌐 Multi-language support: Chinese / English
Automatically remembers your last selected language
Database

Uses SQLite (rental.db) as backend, safe & stable
First run automatically migrates existing JSON data → SQLite
Easy backup and restore (just copy rental.db)
Modern UI

Flat, clean, modern interface
Includes a custom icon (Ezown Car Rental Logo)
Can be bundled into a standalone .exe application
