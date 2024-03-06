"""populate user

Revision ID: 451338bfe5a7
Revises: 2cd092a5120d
Create Date: 2024-03-06 00:38:17.798519

"""
from datetime import datetime
from passlib.hash import pbkdf2_sha512
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData, Table

# revision identifiers, used by Alembic.
revision: str = '451338bfe5a7'
down_revision: Union[str, None] = '2cd092a5120d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

code = pbkdf2_sha512.hash("P0K@852@@admin741$#")
now = datetime.now()
user_data = [
    {
        "username": "pokemon@pokeservice.com.br",
        "password": code,
        "first_access_done": True,
        "double_factor_type": 1,
        "type_user": 0,
        'created_at': now,
        'updated_at': now,
        'language': 'pt',
        'first_name': 'Poke',
        'lastname': 'Pokemon',
        'complete_name': 'Poke Pokemon'
    }
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    meta = MetaData()
    meta.reflect(bind=op.get_bind(), only=('user',))
    user_table = Table('user', meta)
    op.bulk_insert(user_table, user_data)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    meta = MetaData()
    meta.reflect(bind=op.get_bind(), only=('user',))
    user_table = Table('user', meta)
    op.execute(user_table.delete().where(
        user_table.c.username == 'pokemon@pokeservice.com.br'))
    # ### end Alembic commands ###
