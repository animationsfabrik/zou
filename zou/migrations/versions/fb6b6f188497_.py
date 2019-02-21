"""empty message

Revision ID: fb6b6f188497
Revises: fc322f908695
Create Date: 2018-09-26 19:38:09.539070

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlalchemy_utils
import uuid

# revision identifiers, used by Alembic.
revision = 'fb6b6f188497'
down_revision = 'fc322f908695'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('playlist', sa.Column('episode_id', sqlalchemy_utils.types.uuid.UUIDType(binary=False), default=uuid.uuid4, nullable=True))
    op.create_foreign_key(None, 'playlist', 'entity', ['episode_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'playlist', type_='foreignkey')
    op.drop_column('playlist', 'episode_id')
    # ### end Alembic commands ###
