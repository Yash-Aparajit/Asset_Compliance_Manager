# 🏭 Asset Compliance Manager (ACM)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-black.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Active%20Development-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Asset Compliance Manager (ACM)** is a **factory-grade asset compliance and maintenance tracking system** built for **real industrial operations**, not CMMS theory.

The system enforces **strict business rules**, **audit-safe data handling**, and **non-destructive history**, making it suitable for **manufacturing plants, QA environments, and compliance-driven organizations**.

---

## 🎯 Core Objectives

- Maintain a **single source of truth** for assets
- Enforce **compliance-first workflows**
- Preserve **permanent audit history**
- Prevent unsafe or invalid operations by design
- Support **repeatable imports and long-term usage**

---

## 🚀 Features

### ✅ Asset Management
- Centralized asset master
- Unique `asset_code` enforced
- Asset states: Active / Inactive / Scrapped
- Scrapped assets are locked from operations
- Excel-based bulk import (safe & repeatable)

---

### ✅ AMC (Annual Maintenance Contract)
- Exactly **one active AMC per asset**
- Start–end date lifecycle tracking
- Auto status: Active / Overdue / Expired
- AMC events (cost & remarks)
- AMC document uploads (PDF only)
- System-controlled, collision-safe filenames
- Permanent AMC history

---

### ✅ Calibration
- Record-based system (not lifecycle-based)
- Each calibration is a permanent record
- Tracks last calibration & next due date
- Calibration events
- Calibration documents
- Designed for audit traceability

---

### ✅ Events System
- Events belong to either AMC or Calibration
- Events are immutable
- Cost & remarks supported
- Full audit trail

---

### ✅ Document Management
- PDF-only uploads
- System-generated filenames
- Collision-safe versioning
- Linked to AMC or Calibration
- Browser-based document viewer

---

### ✅ Asset Import (Excel → Database)
- Downloadable Excel template
- Indian date format supported (`dd/mm/yyyy`)
- Full transaction rollback on error
- UPSERT logic using `asset_code`
- Safe to run multiple times
- Accessible to multiple roles

---

## 🔒 System Rules (Non-Negotiable)

### AMC Rules
- ❌ Multiple active AMCs per asset — blocked
- ❌ AMC for scrapped asset — blocked
- ❌ Manual document naming — blocked

### Calibration Rules
- Calibration is **not** a lifecycle
- Every calibration is a permanent record
- History is never overwritten or deleted

### Event Rules
- Event must belong to **exactly one context**
- Events cannot be edited or deleted

### Document Rules
- PDF only
- System-controlled filenames
- No silent overwrites

---

## 🧱 Project Structure

```text
Asset Compliance Manager
├── data/
│   ├── AMC/
│   └── Calibration/
├── instance/
├── static/
│   ├── css/
│   └── js/
├── templates/
├── uploads/
├── app.db
├── app.py
├── models.py
└── requirements.txt

---

⚙️ Tech Stack

-Backend: Flask
-ORM: SQLAlchemy
-Database: SQLite (PostgreSQL planned)
-Frontend: Jinja2 + Bootstrap
-Excel Handling: Pandas + OpenPyXL

---

🛠️ Setup Instructions

- git clone https://github.com/your-username/asset-compliance-manager.git
- cd asset-compliance-manager

- python -m venv venv
- Windows: venv\Scripts\activate

- pip install -r requirements.txt

- python app.py
