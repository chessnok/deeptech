from sqlalchemy import MetaData, Table, Column, VARCHAR, UUID, ForeignKey
from sqlalchemy.dialects import postgresql

metadata = MetaData()

User = Table(
    'user',
    metadata,
    Column('id', UUID, primary_key=True),
    Column('first_name', VARCHAR(100), nullable=False),
    Column('conversation_id', UUID, nullable=False),
)
