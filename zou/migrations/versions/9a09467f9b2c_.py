"""empty message

Revision ID: 9a09467f9b2c
Revises: 556526e47daa
Create Date: 2019-03-24 15:57:20.014262

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils
import uuid

# revision identifiers, used by Alembic.
revision = '9a09467f9b2c'
down_revision = '556526e47daa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organisation',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), default=uuid.uuid4, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('hours_by_day', sa.Integer(), nullable=False),
    sa.Column('has_avatar', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('organisation')
    # ### end Alembic commands ###
