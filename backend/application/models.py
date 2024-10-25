import uuid
from datetime import datetime

from application import db

from sqlalchemy.dialects.postgresql import UUID


class Conversation(db.Model):
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    messages = db.relationship("Message", backref="conversation", lazy=True)

    def __repr__(self):
        return f"<Conversation {self.uuid}>"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    author = db.Column(db.Boolean, nullable=False)
    conversation = db.Column(UUID(as_uuid=True),
                             db.ForeignKey("conversation.uuid"),
                             nullable=False)

    def __repr__(self):
        return f"<Message {self.id}>"


class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(32), unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    expires = db.Column(db.DateTime, nullable=True)

    def __init__(self, key, expires):
        self.key = key
        self.expires = expires

    def __repr__(self):
        return f"<ApiKey {self.key}>"
    
    def is_expired(self):
        if not self.expires:
            return False
        if self.expires < datetime.now():
            self.active = False
            return True
        return False

    @staticmethod
    def check_api_key(api_key):
        api_key = ApiKey.query.filter_by(key=api_key).first()
        if not api_key:
            return False
        if api_key.is_expired():
            api_key.active = False
            return False
        return True
