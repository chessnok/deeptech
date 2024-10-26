from sqlalchemy import MetaData, Table, Column, UUID, INTEGER

metadata = MetaData()

User = Table(
    'user',
    metadata,
    Column('tg_id', INTEGER, primary_key=True),
    Column('conversation_id', UUID, nullable=False),
)

Message_author_map = Table(
    'message_author_map',
    metadata,
    Column('message_id', INTEGER, primary_key=True),
    Column('author_id', INTEGER),
)
