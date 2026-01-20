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
    
