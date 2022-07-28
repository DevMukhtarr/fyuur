"""empty message

Revision ID: d1abd0f3f886
Revises: 62b1e08c1abc
Create Date: 2022-05-30 14:18:08.064396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1abd0f3f886'
down_revision = '62b1e08c1abc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.ARRAY(sa.String(120)))
    op.alter_column('Venue', 'genres',
               existing_type=sa.ARRAY(sa.String(120)))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'genres',
               existing_type=sa.ARRAY(sa.String(120)))
    op.alter_column('Artist', 'genres',
               existing_type=sa.ARRAY(sa.String(120)))
    # ### end Alembic commands ###