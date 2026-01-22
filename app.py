from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from models import db, User, Asset, AMC, AMCEvent, AMCDocument, Calibration, CalibrationEvent, CalibrationDocument
from datetime import datetime, date

import pandas as pd
import os

from openpyxl import Workbook
from io import BytesIO


# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "acm-secret-key-change-later"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# -------------------------------------------------
# FILE STORAGE PATHS
# -------------------------------------------------
DATA_DIR = os.path.join(BASE_DIR, "data")
AMC_DOC_DIR = os.path.join(DATA_DIR, "AMC")

os.makedirs(AMC_DOC_DIR, exist_ok=True)

CALIBRATION_DOC_DIR = os.path.join(DATA_DIR, "Calibration")
os.makedirs(CALIBRATION_DOC_DIR, exist_ok=True)

# -------------------------------------------------
# Utility Helpers
# -------------------------------------------------

def format_date_indian(date_obj):
    if not date_obj:
        return "-"
    return date_obj.strftime("%d/%m/%Y")


app.jinja_env.globals.update(
    format_date_indian=format_date_indian
)

def parse_indian_date(val):
    if val in (None, "", pd.NaT):
        return None

    # Excel already parsed it
    if isinstance(val, (datetime, date)):
        return val.date() if isinstance(val, datetime) else val

    val = str(val).strip()

    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(val, fmt).date()
        except Exception:
            continue

    return None

def get_amc_status(amc):
    today = date.today()
    days_left = (amc.end_date - today).days

    if amc.is_completed:
        return ("completed", "Completed")

    if amc.is_cancelled:
        return ("cancelled", "Cancelled")

    if days_left < 0:
        return ("overdue", "Overdue")

    if days_left <= 30:
        return ("warning", "Expiring Soon")

    return ("active", "Active")

# -------------------------------------------------
# ASSET IMPORT SCHEMA
# -------------------------------------------------

ASSET_IMPORT_COLUMNS = {
    "Asset Code": "asset_code",
    "Asset Name": "asset_name",
    "Serial No": "serial_no",
    "Plant": "plant",
    "Department": "department",
    "Location": "location",
    "Purchase Date (DD/MM/YYYY)": "purchase_date",
}


# -------------------------------------------------
# AUTH HELPERS
# -------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def role_required(roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") not in roles:
                flash("Access denied", "danger")
                return redirect(url_for("asset_master"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


# -------------------------------------------------
# INITIAL DB + USER SEED
# -------------------------------------------------
def seed_users():
    users = [
        {
            "username": "developer",
            "password": "dev@123@123",
            "role": "developer"
        },
        {
            "username": "purchase",
            "password": "purchase@jeena",
            "role": "purchase"
        }
    ]

    for u in users:
        existing = User.query.filter_by(username=u["username"]).first()
        if not existing:
            user = User(
                username=u["username"],
                password_hash=generate_password_hash(u["password"]),
                role=u["role"]
            )
            db.session.add(user)

    db.session.commit()


with app.app_context():
    db.create_all()
    seed_users()


# -------------------------------------------------
# LOGIN / LOGOUT
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username, is_active=True).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials", "danger")
            return render_template("login.html")

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role

        return redirect(url_for("asset_master"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------------------------------
# ASSET MASTER
# -------------------------------------------------
@app.route("/assets")
@login_required
def asset_master():
    query = Asset.query

    search = request.args.get("search")
    plant = request.args.get("plant")
    department = request.args.get("department")
    status = request.args.get("status")

    if search:
        query = query.filter(
            (Asset.asset_code.ilike(f"%{search}%")) |
            (Asset.asset_name.ilike(f"%{search}%")) |
            (Asset.serial_no.ilike(f"%{search}%"))
        )

    if plant:
        query = query.filter(Asset.plant == plant)

    if department:
        query = query.filter(Asset.department == department)

    if status:
        query = query.filter(Asset.status == status)

    assets = query.order_by(Asset.id.asc()).all()

    return render_template("asset_master.html", assets=assets)


# -------------------------------------------------
# ADD ASSET
# -------------------------------------------------
@app.route("/assets/add", methods=["GET", "POST"])
@login_required
def add_asset():
    if request.method == "POST":
        asset_code = request.form.get("asset_code", "").strip()

        if Asset.query.filter_by(asset_code=asset_code).first():
            flash("Asset Code already exists", "danger")
            return render_template("asset_add.html")

        # ---- DATE PARSING (ONLY PLACE) ----
        purchase_date_str = request.form.get("purchase_date")
        if purchase_date_str:
            purchase_date = datetime.strptime(
                purchase_date_str, "%Y-%m-%d"
            ).date()
        else:
            purchase_date = None
        # ----------------------------------

        asset = Asset(
            asset_code=asset_code,
            asset_name=request.form.get("asset_name"),
            serial_no=request.form.get("serial_no"),
            plant=request.form.get("plant"),
            department=request.form.get("department"),
            location=request.form.get("location"),
            purchase_date=purchase_date   # ✅ DATE OBJECT ONLY
        )

        db.session.add(asset)
        db.session.commit()

        flash("Asset added successfully", "success")
        return redirect(url_for("asset_master"))

    return render_template("asset_add.html")


# -------------------------------------------------
# EDIT ASSET (NO STATUS CHANGE)
# -------------------------------------------------
@app.route("/assets/edit/<int:asset_id>", methods=["GET", "POST"])
@login_required
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)

    if request.method == "POST":
        new_code = request.form.get("asset_code").strip()

        if new_code != asset.asset_code:
            if Asset.query.filter_by(asset_code=new_code).first():
                flash("Asset Code already exists", "danger")
                return render_template("asset_edit.html", asset=asset)

        asset.asset_code = new_code
        asset.asset_name = request.form.get("asset_name")
        asset.serial_no = request.form.get("serial_no")
        asset.plant = request.form.get("plant")
        asset.department = request.form.get("department")
        asset.location = request.form.get("location")
        purchase_date_str = request.form.get("purchase_date")

        if purchase_date_str:
            asset.purchase_date = datetime.strptime(
                purchase_date_str, "%Y-%m-%d"
            ).date()
        else:
            asset.purchase_date = None

        db.session.commit()

        flash("Asset updated successfully", "success")
        return redirect(url_for("asset_master"))

    return render_template("asset_edit.html", asset=asset)


# -------------------------------------------------
# Asset Import
# -------------------------------------------------

@app.route("/assets/import", methods=["GET", "POST"])
@login_required
def import_assets():
    if request.method == "POST":
        file = request.files.get("file")

        # ---------- FILE CHECK ----------
        if not file or not file.filename.lower().endswith(".xlsx"):
            flash("Please upload a valid .xlsx Excel file", "danger")
            return redirect(url_for("import_assets"))

        try:
            df = pd.read_excel(file)
        except Exception:
            flash("Unable to read Excel file. File may be corrupted.", "danger")
            return redirect(url_for("import_assets"))

        # ---------- EMPTY FILE CHECK ----------
        if df.empty:
            flash(
                "Excel file contains no data rows. Please add asset data below the header.",
                "warning"
            )
            return redirect(url_for("import_assets"))

        # ---------- COLUMN VALIDATION ----------
        uploaded_columns = [str(c).strip() for c in df.columns]
        expected_columns = list(ASSET_IMPORT_COLUMNS.keys())

        missing = set(expected_columns) - set(uploaded_columns)
        if missing:
            flash(f"Missing columns: {', '.join(missing)}", "danger")
            return redirect(url_for("import_assets"))

        # Rename columns
        df = df.rename(columns=ASSET_IMPORT_COLUMNS)

        valid_rows = []
        invalid_rows = []

        seen_codes = set()
        existing_codes = {
            a.asset_code
            for a in Asset.query.with_entities(Asset.asset_code).all()
        }

        # ---------- ROW VALIDATION ----------
        for idx, row in df.iterrows():
            # Skip fully empty rows
            if row.isna().all():
                continue

            errors = []

            asset_code = row.get("asset_code")
            asset_name = row.get("asset_name")

            asset_code = str(asset_code).strip() if pd.notna(asset_code) else ""
            asset_name = str(asset_name).strip() if pd.notna(asset_name) else ""

            if not asset_code:
                errors.append("Missing Asset Code")
            if not asset_name:
                errors.append("Missing Asset Name")

            if asset_code:
                if asset_code in seen_codes:
                    errors.append("Duplicate Asset Code in file")
                if asset_code in existing_codes:
                    errors.append("Asset Code already exists")

            if asset_code:
                seen_codes.add(asset_code)

            purchase_date = None
            raw_date = row.get("purchase_date")

            if raw_date not in (None, "", pd.NaT):
                parsed_date = parse_indian_date(raw_date)
                purchase_date = parsed_date.isoformat() if parsed_date else None

                if not purchase_date:
                    errors.append("Invalid Purchase Date (DD/MM/YYYY or DD-MM-YYYY)")

                if parsed_date and parsed_date > date.today():
                    errors.append("Purchase Date cannot be in the future")

            record = {
                "row_no": idx + 2,
                "asset_code": asset_code,
                "asset_name": asset_name,
                "serial_no": (
                    str(row.get("serial_no")).strip()
                    if row.get("serial_no") not in (None, "", pd.NaT) else None
                ),
                "plant": row.get("plant"),
                "department": row.get("department"),
                "location": row.get("location"),
                "purchase_date": purchase_date,
            }

            if errors:
                record["errors"] = errors
                invalid_rows.append(record)
            else:
                valid_rows.append(record)

        # ---------- FINAL SAFETY GUARD ----------
        if not valid_rows and not invalid_rows:
            flash(
                "All rows in the file are empty. Please enter asset details and try again.",
                "warning"
            )
            return redirect(url_for("import_assets"))

        if not valid_rows and invalid_rows:
            flash(
                "All rows are invalid. Please fix errors and re-upload the file.",
                "danger"
            )
            return redirect(url_for("import_assets"))

        session["import_valid"] = valid_rows
        session.modified = True

        return render_template(
            "asset_import.html",
            valid_rows=valid_rows,
            invalid_rows=invalid_rows
        )

    return render_template("asset_import.html")


@app.route("/assets/import/confirm", methods=["POST"])
@login_required
def confirm_import():
    rows = session.pop("import_valid", [])

    if not rows:
        flash("No validated rows found to import.", "danger")
        return redirect(url_for("import_assets"))

    try:
        imported_count = 0
        for r in rows:

            if Asset.query.filter_by(asset_code=r["asset_code"]).first():
                continue
            asset = Asset(
                asset_code=r["asset_code"],
                asset_name=r["asset_name"],
                serial_no=r.get("serial_no"),
                plant=r.get("plant"),
                department=r.get("department"),
                location=r.get("location"),
                purchase_date=(
                    datetime.fromisoformat(r["purchase_date"]).date()
                    if r.get("purchase_date") else None
                ),
            )
            db.session.add(asset)
            imported_count += 1
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f"Import failed: {str(e)}", "danger")
        return redirect(url_for("import_assets"))


    flash(f"{imported_count} assets imported successfully", "success")
    return redirect(url_for("asset_master"))


# -------------------------------------------------
# DOWNLOAD ASSET IMPORT TEMPLATE
# -------------------------------------------------
@app.route("/assets/import/template")
@login_required
def download_asset_template():
    wb = Workbook()
    ws = wb.active
    ws.title = "Asset Import Template"

    headers = [
        "Asset Code",
        "Asset Name",
        "Serial No",
        "Plant",
        "Department",
        "Location",
        "Purchase Date (DD/MM/YYYY)"
    ]

    ws.append(headers)

    # Style header row (basic, readable)
    for col in range(1, len(headers) + 1):
        ws.cell(row=1, column=col).font = ws.cell(
            row=1, column=col
        ).font.copy(bold=True)
        ws.column_dimensions[chr(64 + col)].width = 22

    # Example row (optional but recommended)
    ws.append([
        "A001",
        "Hydraulic Press",
        "HP-8891",
        "Plant-1",
        "Production",
        "Line-3",
        "17/01/2026"
    ])

    # Prepare file in memory
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="ACM_Asset_Import_Template.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# -------------------------------------------------
# AMC CREATE + ACTIVE LIST
# -------------------------------------------------
@app.route("/amc", methods=["GET", "POST"])
@login_required
def amc_create():
    assets = Asset.query.order_by(Asset.id.asc()).all()

    active_amcs = (
        AMC.query
        .filter_by(is_completed=False, is_cancelled=False)
        .all()
    )

    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        yearly_cost = request.form.get("yearly_cost")

        # ---------- VALIDATIONS ----------
        asset = Asset.query.get(asset_id)
        if not asset:
            flash("Invalid asset selected", "danger")
            return redirect(url_for("amc_create"))

        if asset.status == "Scrapped":
            flash("Cannot create AMC for scrapped asset", "danger")
            return redirect(url_for("amc_create"))

        existing_amc = AMC.query.filter_by(
            asset_id=asset.id,
            is_completed=False,
            is_cancelled=False
        ).first()

        if existing_amc:
            flash("Active AMC already exists for this asset", "danger")
            return redirect(url_for("amc_create"))

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except Exception:
            flash("Invalid date format", "danger")
            return redirect(url_for("amc_create"))

        if start_date >= end_date:
            flash("Start date must be before end date", "danger")
            return redirect(url_for("amc_create"))

        # ---------- CREATE ----------
        amc = AMC(
            asset_id=asset.id,
            start_date=start_date,
            end_date=end_date,
            yearly_cost=float(yearly_cost) if yearly_cost else None
        )

        db.session.add(amc)
        db.session.commit()

        flash("AMC created successfully", "success")
        return redirect(url_for("amc_view", amc_id=amc.id))

    amc_status_map = {}
    today = date.today()

    for amc in active_amcs:
        status_key, status_label = get_amc_status(amc)
        days_left = (amc.end_date - today).days

        amc_status_map[amc.id] = {
            "key": status_key,
            "label": status_label,
            "days_left": days_left
        }


    return render_template(
        "amc_create.html",
        assets=assets,
        active_amcs=active_amcs,
        amc_status_map=amc_status_map
    )


# -------------------------------------------------
# AMC VIEW
# -------------------------------------------------
@app.route("/amc/<int:amc_id>")
@login_required
def amc_view(amc_id):
    amc = AMC.query.get_or_404(amc_id)
    asset = amc.asset

    today = date.today()
    days_left = (amc.end_date - today).days

    status_key, status_label = get_amc_status(amc)

    asset_age = None
    if asset.purchase_date:
        asset_age = (today - asset.purchase_date).days

    # ---- AMC TOTAL SPEND CALCULATION ----
    event_total = sum(
        e.cost or 0
        for e in amc.events
    )

    contract_value = amc.yearly_cost or 0
    total_spend = contract_value + event_total

    return render_template(
        "amc_view.html",
        amc=amc,
        asset=asset,
        status_key=status_key,
        status_label=status_label,
        asset_age=asset_age,
        days_left=days_left,
        contract_value=contract_value,
        event_total=event_total,
        total_spend=total_spend,
        today=today
    )


# -------------------------------------------------
# AMC EVENT CREATE
# -------------------------------------------------
@app.route("/amc/<int:amc_id>/event", methods=["POST"])
@login_required
def amc_add_event(amc_id):
    amc = AMC.query.get_or_404(amc_id)

    if amc.is_completed or amc.is_cancelled:
        flash("Cannot add event to closed AMC", "danger")
        return redirect(url_for("amc_view", amc_id=amc.id))

    event_date = request.form.get("event_date")
    remarks = request.form.get("remarks")
    cost = request.form.get("cost")

    try:
        event_date = datetime.strptime(event_date, "%Y-%m-%d").date()
    except Exception:
        flash("Invalid event date", "danger")
        return redirect(url_for("amc_view", amc_id=amc.id))

    event = AMCEvent(
        amc_id=amc.id,
        event_date=event_date,
        remarks=remarks,
        cost=float(cost) if cost else None
    )

    db.session.add(event)
    db.session.commit()

    flash("AMC event added successfully", "success")
    return redirect(url_for("amc_view", amc_id=amc.id))


# -------------------------------------------------
# AMC DOCUMENT UPLOAD
# -------------------------------------------------
@app.route("/amc/<int:amc_id>/document", methods=["POST"])
@login_required
def amc_upload_document(amc_id):
    amc = AMC.query.get_or_404(amc_id)

    if amc.is_completed or amc.is_cancelled:
        flash("Cannot upload document to closed AMC", "danger")
        return redirect(url_for("amc_view", amc_id=amc.id))

    file = request.files.get("file")
    doc_type = request.form.get("document_type")

    if doc_type == "Other":
        doc_type = request.form.get("other_document_type", "").strip()
        if not doc_type:
            flash("Please specify document type", "danger")
            return redirect(url_for("amc_view", amc_id=amc.id))


    if not file or not file.filename.lower().endswith(".pdf"):
        flash("Only PDF files are allowed", "danger")
        return redirect(url_for("amc_view", amc_id=amc.id))

    asset_code = amc.asset.asset_code
    month_year = datetime.today().strftime("%m-%Y")

    safe_doc_type = doc_type.replace(" ", "_")

    # ---- sequence per AMC + document type ----
    existing_count = AMCDocument.query.filter_by(
        amc_id=amc.id,
        document_type=doc_type
    ).count()

    seq = existing_count + 1

    stored_filename = (
        f"{month_year}_AMC_{asset_code}_{safe_doc_type}_{seq}.pdf"
    )

    file_path = os.path.join(AMC_DOC_DIR, stored_filename)

    file.save(file_path)

    doc = AMCDocument(
        amc_id=amc.id,
        document_type=doc_type,
        stored_filename=stored_filename,
        original_filename=file.filename
    )

    db.session.add(doc)
    db.session.commit()

    flash("Document uploaded successfully", "success")
    return redirect(url_for("amc_view", amc_id=amc.id))


# -------------------------------------------------
# AMC DOCUMENT DOWNLOAD
# -------------------------------------------------
@app.route("/amc/document/<int:doc_id>/download")
@login_required
def amc_download_document(doc_id):
    doc = AMCDocument.query.get_or_404(doc_id)

    file_path = os.path.join(AMC_DOC_DIR, doc.stored_filename)

    if not os.path.exists(file_path):
        flash("File not found on server", "danger")
        return redirect(url_for("amc_view", amc_id=doc.amc_id))

    return send_file(
        file_path,
        as_attachment=False,
        mimetype="application/pdf"
    )


# -------------------------------------------------
# AMC COMPLETE
# -------------------------------------------------
@app.route("/amc/<int:amc_id>/complete", methods=["GET", "POST"])
@login_required
def amc_complete(amc_id):
    amc = AMC.query.get_or_404(amc_id)

    if amc.is_completed or amc.is_cancelled:
        flash("AMC already closed", "warning")
        return redirect(url_for("amc_view", amc_id=amc.id))

    amc.is_completed = True
    amc.completed_on = date.today()

    db.session.commit()

    flash("AMC marked as completed", "successfully !!")
    return redirect(url_for("amc_create"))


# -------------------------------------------------
# AMC CANCEL
# -------------------------------------------------
@app.route("/amc/<int:amc_id>/cancel", methods=["GET", "POST"])
@login_required
def amc_cancel(amc_id):
    amc = AMC.query.get_or_404(amc_id)

    if amc.is_completed or amc.is_cancelled:
        flash("AMC already closed", "warning")
        return redirect(url_for("amc_view", amc_id=amc.id))

    amc.is_cancelled = True
    amc.completed_on = date.today()

    db.session.commit()

    flash("AMC marked as cancelled", "successfully !!")
    return redirect(url_for("amc_create"))


# -------------------------------------------------
# CALIBRATION MAIN PAGE
# -------------------------------------------------

@app.route("/calibration")
@login_required
def calibration():
    assets = Asset.query.order_by(Asset.id.asc()).all()
    return render_template("calibration.html", assets=assets)

@app.route("/calibration/asset/<int:asset_id>")
@login_required
def calibration_asset_data(asset_id):
    asset = Asset.query.get_or_404(asset_id)

    latest = (
        Calibration.query
        .filter_by(asset_id=asset.id)
        .order_by(
            Calibration.calibration_done_date.desc(),
            Calibration.created_on.desc()
        )
        .first()
    )

    today = date.today()

    asset_age = (
        (today - asset.purchase_date).days
        if asset.purchase_date else None
    )

    if latest:
        last_done = format_date_indian(latest.calibration_done_date)
        next_due = format_date_indian(latest.next_due_date)
        days_left = (latest.next_due_date - today).days
    else:
        last_done = next_due = days_left = "-"

    return {
        "asset": {
            "id": asset.id,
            "asset_code": asset.asset_code,
            "asset_name": asset.asset_name,
            "serial_no": asset.serial_no,
            "plant": asset.plant,
            "department": asset.department,
            "location": asset.location,
            "purchase_date": format_date_indian(asset.purchase_date),
        },
        "asset_age": asset_age,
        "last_done": last_done,
        "next_due": next_due,
        "days_left": days_left,
    }

@app.route("/calibration/save", methods=["POST"])
@login_required
def save_calibration():
    asset_id = request.form.get("asset_id")
    asset = Asset.query.get_or_404(asset_id)

    if asset.status == "Scrapped":
        flash("Cannot record calibration for scrapped asset", "danger")
        return redirect(url_for("calibration"))

    done_date = datetime.strptime(
        request.form["calibration_done_date"], "%Y-%m-%d"
    ).date()

    next_due = datetime.strptime(
        request.form["next_due_date"], "%Y-%m-%d"
    ).date()

    if next_due <= done_date or next_due <= date.today():
        flash("Invalid next calibration due date", "danger")
        return redirect(url_for("calibration"))

    try:
        cal = Calibration(
            asset_id=asset.id,
            calibration_done_date=done_date,
            next_due_date=next_due,
            cost=request.form.get("cost") or None,
            remarks=request.form.get("remarks"),
        )

        db.session.add(cal)
        db.session.flush()   

        # --------------------
        # DOCUMENTS
        # --------------------
        files = request.files
        doc_index = 0

        while True:
            file = files.get(f"documents[{doc_index}][file]")
            if not file:
                break

            doc_type = request.form.get(f"documents[{doc_index}][type]")
            stored_filename = os.path.basename(
                request.form.get(f"documents[{doc_index}][filename]")
            )

            file_path = os.path.join(CALIBRATION_DOC_DIR, stored_filename)
            file.save(file_path)

            doc = CalibrationDocument(
                calibration_id=cal.id,
                document_type=doc_type,
                stored_filename=stored_filename,
                original_filename=file.filename
            )

            db.session.add(doc)
            doc_index += 1

        # --------------------
        # EVENTS
        # --------------------
        idx = 0
        while f"event_date_{idx}" in request.form:
            event = CalibrationEvent(
                calibration_id=cal.id,
                event_date=datetime.strptime(
                    request.form[f"event_date_{idx}"], "%Y-%m-%d"
                ).date(),
                remarks=request.form.get(f"event_remarks_{idx}"),
                cost=request.form.get(f"event_cost_{idx}") or None
            )
            db.session.add(event)
            idx += 1

        # --------------------
        # FINAL COMMIT
        # --------------------
        db.session.commit()
    
        flash("Calibration recorded successfully", "success")
        return redirect(url_for("calibration"))

    except Exception as e:
        db.session.rollback()
        flash("Calibration save failed. No data was recorded.", "danger")
        return redirect(url_for("calibration"))

 
# -------------------------------------------------
# HISTORY ROUTES
# -------------------------------------------------
    
@app.route("/history")
@login_required
def history():
    assets = Asset.query.order_by(Asset.asset_code.asc()).all()

    asset_id = request.args.get("asset_id")
    status = request.args.get("status")  # completed / cancelled / all

    query = AMC.query.join(Asset)

    # ---- HARD RULE: ONLY CLOSED AMC ----
    query = query.filter(
        (AMC.is_completed == True) | (AMC.is_cancelled == True)
    )

    if asset_id:
        query = query.filter(AMC.asset_id == asset_id)

    if status == "completed":
        query = query.filter(AMC.is_completed == True)

    if status == "cancelled":
        query = query.filter(AMC.is_cancelled == True)

    amcs = query.order_by(AMC.completed_on.desc()).all()

    return render_template(
        "history_amc_list.html",
        assets=assets,
        amcs=amcs,
        selected_asset=asset_id,
        selected_status=status
    )

@app.route("/history/amc/<int:amc_id>")
@login_required
def history_amc_view(amc_id):
    amc = AMC.query.get_or_404(amc_id)

    # ---- SAFETY GUARD ----
    if not amc.is_completed and not amc.is_cancelled:
        flash("Active AMC cannot be viewed in history", "danger")
        return redirect(url_for("history"))

    asset = amc.asset

    event_total = sum(e.cost or 0 for e in amc.events)
    contract_value = amc.yearly_cost or 0
    total_spend = contract_value + event_total

    asset_age = None
    if asset.purchase_date:
        asset_age = (date.today() - asset.purchase_date).days

    return render_template(
        "history_amc_view.html",
        amc=amc,
        asset=asset,
        asset_age=asset_age,
        contract_value=contract_value,
        event_total=event_total,
        total_spend=total_spend
    )

@app.route("/history/amc/<int:amc_id>/export")
@login_required
def export_amc_history(amc_id):
    amc = AMC.query.get_or_404(amc_id)

    if not amc.is_completed and not amc.is_cancelled:
        flash("Active AMC cannot be exported", "danger")
        return redirect(url_for("history"))

    import zipfile
    from io import BytesIO
    import pandas as pd

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:

        # -------- SUMMARY EXCEL --------
        summary = {
            "Asset Code": amc.asset.asset_code,
            "Asset Name": amc.asset.asset_name,
            "AMC Start": format_date_indian(amc.start_date),
            "AMC End": format_date_indian(amc.end_date),
            "Status": "Completed" if amc.is_completed else "Cancelled",
            "Contract Value": amc.yearly_cost or 0,
        }

        df_summary = pd.DataFrame([summary])
        summary_xlsx = BytesIO()
        df_summary.to_excel(summary_xlsx, index=False)
        z.writestr("summary/amc_summary.xlsx", summary_xlsx.getvalue())

        # -------- EVENTS EXCEL --------
        events = [{
            "Date": format_date_indian(e.event_date),
            "Remarks": e.remarks,
            "Cost": e.cost
        } for e in amc.events]

        df_events = pd.DataFrame(events)
        events_xlsx = BytesIO()
        df_events.to_excel(events_xlsx, index=False)
        z.writestr("events/amc_events.xlsx", events_xlsx.getvalue())

        # -------- DOCUMENTS --------
        for d in amc.documents:
            path = os.path.join(AMC_DOC_DIR, d.stored_filename)
            if os.path.exists(path):
                z.write(
                    path,
                    arcname=f"documents/{d.stored_filename}"
                )

    buffer.seek(0)

    filename = f"AMC_{amc.asset.asset_code}_{amc.id}.zip"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/zip"
    )

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
