from typing import List
import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped

from application import db

from sqlalchemy.dialects.postgresql import UUID


class Conversation(db.Model):
    __tablename__ = "conversation"

    uuid = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    messages : Mapped[List["Message"]] = db.relationship(back_populates="conversation")

    def __repr__(self):
        return f"<Conversation {self.uuid}>"


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    author = db.Column(db.Boolean, nullable=False)
    conversation_id = db.mapped_column(db.ForeignKey("conversation.uuid"))
    conversation = db.relationship("Conversation", back_populates="messages")


    def __repr__(self):
        return f"<Message {self.id}>"


from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime


class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    expires = db.Column(db.DateTime, nullable=True)

    # Соль, добавляемая перед хешированием
    salt = "your_tupaya_salt"

    def __init__(self, key, expires):
        self.set_apikey(key)
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

    def set_apikey(self, raw_key):
        """Хеширует апикей с солью и сохраняет его."""
        salted_key = f"{self.salt}{raw_key}"
        self.key = generate_password_hash(salted_key)

    @staticmethod
    def check_api_key(raw_key):
        """Проверяет хешированный апикей с солью."""
        api_key_entry = ApiKey.query.filter_by(active=True).first()
        if not api_key_entry:
            return False
        if api_key_entry.is_expired():
            api_key_entry.active = False
            db.session.commit()
            return False
        salted_key = f"{api_key_entry.salt}{raw_key}"
        return check_password_hash(api_key_entry.key, salted_key)
