from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError

from .models import Blacklist, BlacklistInputSchema, BlacklistSchema, db

input_schema = BlacklistInputSchema()
output_schema = BlacklistSchema()


def client_ip():
    """Detrás del load balancer de Beanstalk, la IP real viene en X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


class BlacklistCreate(Resource):
    @jwt_required()
    def post(self):
        try:
            data = input_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"msg": "Datos inválidos.", "errors": err.messages}, 400

        email = data["email"].strip().lower()
        if Blacklist.query.filter_by(email=email).first():
            return {"msg": f"El email {email} ya está en la lista negra global."}, 409

        entry = Blacklist(
            email=email,
            app_uuid=data["app_uuid"],
            blocked_reason=data.get("blocked_reason"),
            request_ip=client_ip(),
        )
        db.session.add(entry)
        db.session.commit()
        return {
            "msg": f"El email {email} fue agregado a la lista negra global.",
            "data": output_schema.dump(entry),
        }, 201


class BlacklistCheck(Resource):
    @jwt_required()
    def get(self, email):
        entry = Blacklist.query.filter_by(email=email.strip().lower()).first()
        return {
            "is_blacklisted": entry is not None,
            "blocked_reason": entry.blocked_reason if entry else None,
        }, 200


class Ping(Resource):
    """Health check para Beanstalk. Sin token, para que el balanceador pueda consultarlo."""

    def get(self):
        return {"status": "ok", "version": current_app.config["APP_VERSION"]}, 200
