from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# -------------------------
# USER / AUTH
# -------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False
    )  # 'developer' or 'purchase'

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# -------------------------
# ASSET (CORE ENTITY)
# -------------------------
class Asset(db.Model):
    __tablename__ = "assets"

    # SYSTEM ID (TRUTH)
    id = db.Column(db.Integer, primary_key=True)

    # BUSINESS IDENTIFIER (EDITABLE)
    asset_code = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    asset_name = db.Column(
        db.String(255),
        nullable=False
    )

    serial_no = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    plant = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    department = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    location = db.Column(
        db.String(150),
        nullable=True
    )

    purchase_date = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Active"
    )  # Active / Scrapped

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Asset {self.asset_code} | {self.asset_name}>"
    
# -------------------------
# AMC (ANNUAL MAINTENANCE CONTRACT)
# -------------------------
class AMC(db.Model):
    __tablename__ = "amcs"

    id = db.Column(db.Integer, primary_key=True)

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey("assets.id"),
        nullable=False,
        index=True
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    yearly_cost = db.Column(
        db.Float,
        nullable=True
    )

    is_completed = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    is_cancelled = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    completed_on = db.Column(
        db.Date,
        nullable=True
    )

    created_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # RELATIONSHIP
    asset = db.relationship(
        "Asset",
        backref=db.backref("amcs", lazy=True)
    )

    def __repr__(self):
        return f"<AMC Asset={self.asset_id} {self.start_date} → {self.end_date}>"

# -------------------------
# AMC EVENTS
# -------------------------
class AMCEvent(db.Model):
    __tablename__ = "amc_events"

    id = db.Column(db.Integer, primary_key=True)

    amc_id = db.Column(
        db.Integer,
        db.ForeignKey("amcs.id"),
        nullable=False,
        index=True
    )

    event_date = db.Column(
        db.Date,
        nullable=False
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    cost = db.Column(
        db.Float,
        nullable=True
    )

    created_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    amc = db.relationship(
        "AMC",
        backref=db.backref("events", lazy=True, cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f"<AMCEvent AMC={self.amc_id} {self.event_date}>"

# -------------------------
# AMC DOCUMENTS
# -------------------------
class AMCDocument(db.Model):
    __tablename__ = "amc_documents"

    id = db.Column(db.Integer, primary_key=True)

    amc_id = db.Column(
        db.Integer,
        db.ForeignKey("amcs.id"),
        nullable=False,
        index=True
    )

    document_type = db.Column(
        db.String(100),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    uploaded_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    amc = db.relationship(
        "AMC",
        backref=db.backref("documents", lazy=True, cascade="all, delete-orphan")
    )

    def __repr__(self):
        return f"<AMCDocument {self.stored_filename}>"

# -------------------------
# CALIBRATION (RECORD-BASED)
# -------------------------
class Calibration(db.Model):
    __tablename__ = "calibrations"

    id = db.Column(db.Integer, primary_key=True)

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey("assets.id"),
        nullable=False,
        index=True
    )

    calibration_done_date = db.Column(
        db.Date,
        nullable=False
    )

    next_due_date = db.Column(
        db.Date,
        nullable=False
    )

    cost = db.Column(
        db.Float,
        nullable=True
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    created_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    asset = db.relationship(
        "Asset",
        backref=db.backref("calibrations", lazy=True)
    )

    def __repr__(self):
        return (
            f"<Calibration Asset={self.asset_id} "
            f"{self.calibration_done_date} → {self.next_due_date}>"
        )


# -------------------------
# CALIBRATION EVENTS
# -------------------------
class CalibrationEvent(db.Model):
    __tablename__ = "calibration_events"

    id = db.Column(db.Integer, primary_key=True)

    calibration_id = db.Column(
        db.Integer,
        db.ForeignKey("calibrations.id"),
        nullable=False,
        index=True
    )

    event_date = db.Column(
        db.Date,
        nullable=False
    )

    remarks = db.Column(
        db.Text,
        nullable=True
    )

    cost = db.Column(
        db.Float,
        nullable=True
    )

    created_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    calibration = db.relationship(
        "Calibration",
        backref=db.backref(
            "events",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<CalibrationEvent Cal={self.calibration_id} {self.event_date}>"


# -------------------------
# CALIBRATION DOCUMENTS
# -------------------------

class CalibrationDocument(db.Model):
    __tablename__ = "calibration_documents"

    id = db.Column(db.Integer, primary_key=True)

    calibration_id = db.Column(
        db.Integer,
        db.ForeignKey("calibrations.id"),
        nullable=False,
        index=True
    )

    document_type = db.Column(
        db.String(100),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    uploaded_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    calibration = db.relationship(
        "Calibration",
        backref=db.backref(
            "documents",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    def __repr__(self):
        return f"<CalibrationDocument {self.stored_filename}>"

# -------------------------
# Asset Scrap
# -------------------------

class AssetScrap(db.Model):
    __tablename__ = "asset_scraps"

    id = db.Column(db.Integer, primary_key=True)

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey("assets.id"),
        nullable=False,
        unique=True  # one-time action
    )

    scrap_date = db.Column(db.Date, nullable=False)

    approved_by = db.Column(db.String(150), nullable=False)

    scrap_note_filename = db.Column(db.String(255), nullable=False)

    original_filename = db.Column(db.String(255), nullable=False)

    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship(
        "Asset",
        backref=db.backref("scrap_record", uselist=False)
    )


# -------------------------
# REMINDER ACKNOWLEDGEMENT
# -------------------------

class ReminderAck(db.Model):
    __tablename__ = "reminder_acks"

    id = db.Column(db.Integer, primary_key=True)

    # AMC or Calibration
    source_type = db.Column(
        db.String(20),
        nullable=False,
        index=True
    )  # 'AMC' / 'Calibration'

    # AMC.id or Calibration.id
    source_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    asset_id = db.Column(
        db.Integer,
        db.ForeignKey("assets.id"),
        nullable=False,
        index=True
    )

    rule = db.Column(
        db.String(20),
        nullable=False
    )  
    # 'overdue' / 'due_soon' / 'upcoming'

    acknowledged_on = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    acknowledged_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    # RELATIONSHIPS (quiet, no cascade madness)
    asset = db.relationship("Asset")
    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint(
            "source_type",
            "source_id",
            "rule",
            name="uq_reminder_ack_once"
        ),
    )

    def __repr__(self):
        return (
            f"<ReminderAck {self.source_type} "
            f"{self.source_id} [{self.rule}]>"
        )
