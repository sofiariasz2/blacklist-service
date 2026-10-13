import uuid
from datetime import datetime, timezone

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError, fields, validate

db = SQLAlchemy()
ma = Marshmallow()


class Blacklist(db.Model):
    __tablename__ = "blacklists"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    app_uuid = db.Column(db.String(36), nullable=False)
    blocked_reason = db.Column(db.String(255), nullable=True)
    request_ip = db.Column(db.String(45), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


def validate_uuid(value):
    try:
        uuid.UUID(str(value))
    except ValueError:
        raise ValidationError("Debe ser un UUID válido.")


class BlacklistInputSchema(ma.Schema):
    """Valida el body del POST /blacklists."""

    email = fields.Email(required=True)
    app_uuid = fields.String(required=True, validate=validate_uuid)
    blocked_reason = fields.String(
        required=False, allow_none=True, validate=validate.Length(max=255)
    )


class BlacklistSchema(ma.SQLAlchemyAutoSchema):
    """Serializa un registro guardado."""

    class Meta:
        model = Blacklist
