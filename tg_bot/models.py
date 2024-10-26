from sqlalchemy import MetaData, Table, Column, UUID, INTEGER

metadata = MetaData()

User = Table(
    'user',
    metadata,
    Column('tg_id', INTEGER, primary_key=True),
    Column('conversation_id', UUID, nullable=False),
)
