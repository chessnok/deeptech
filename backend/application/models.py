import uuid

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
