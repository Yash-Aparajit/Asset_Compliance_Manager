# 🏭 Asset Compliance Manager (ACM)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-black.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Asset Compliance Manager (ACM)** is a **factory-grade asset lifecycle & compliance system** built for **real industrial operations**, not CMMS theory.

ACM focuses on **asset accountability**, **maintenance compliance**, and **audit-safe history** with strict business rules and non-destructive data handling.

---

## 🎯 Core Design Philosophy

> **Nothing is deleted. Everything is traceable. Rules > Convenience.**

- AMC is a **lifecycle**
- Calibration is a **recording system**
- Events and documents are **immutable**
- History is **separate from operations**
- Designed for **non-technical factory users**

---

## 🚀 Features

### ✅ Asset Management
- Asset master with unique `asset_code`
- Asset import via Excel (repeatable & safe)
- Asset status: Active / Inactive / Scrapped
- Scrapped assets are locked from operations

---

### ✅ AMC (Annual Maintenance Contract)
- One **active AMC per asset** (hard rule)
- Start–end date lifecycle
- Auto status: Active / Overdue / Expired
- AMC event tracking (cost & remarks)
- AMC document upload (PDF only)
- System-controlled file naming
- Permanent AMC history

---

### ✅ Calibration
- Calibration is **record-based**, not lifecycle-based
- Record calibration for assets
- Track last calibration & next due date
- Calibration events
- Calibration documents
- Permanent history storage

---

### ✅ Events System
- Events belong to **either AMC or Calibration**
- Events are immutable
- Cost & remarks supported
- Full audit trail

---

### ✅ Document Management
- PDF-only uploads
- System-generated filenames
- Collision-safe naming
- Linked to AMC or Calibration
- Browser-based document viewer

---

### ✅ Asset Import (Excel → Database)
- Downloadable Excel template
- Indian date format supported (`dd/mm/yyyy`)
- Full transaction rollback on error
- UPSERT logic using `asset_code`
- Safe to run multiple times
- Available to multiple roles

---

## 🔒 System Rules (Non-Negotiable)

### AMC Rules
- ❌ Multiple active AMCs per asset — blocked
- ❌ AMC for scrapped asset — blocked
- ❌ Manual file naming — blocked

### Calibration Rules
- Calibration is **not** a lifecycle
- Each calibration is a permanent record
- History is preserved forever

### Events
- Must belong to **exactly one context**
- Cannot be edited or deleted

### Documents
- PDF only
- System-generated filenames
- No overwrite without versioning

---

## 🧱 Project Structure



---

## ⚙️ Tech Stack

- **Backend:** Flask
- **ORM:** SQLAlchemy
- **Database:** SQLite (PostgreSQL planned)
- **Frontend:** Jinja2 + Bootstrap
- **Excel Handling:** Pandas + OpenPyXL

---

## 🛠️ Setup Instructions

```bash
git clone https://github.com/your-username/asset-compliance-manager.git
cd asset-compliance-manager

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

python app.py
