"""empty message

Revision ID: e6b1eab432eb
Revises: 
Create Date: 2022-05-28 12:28:45.420427

"""
from tokenize import String
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6b1eab432eb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Artist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('city', sa.String(length=120), nullable=True),
    sa.Column('state', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.Column('genres', sa.ARRAY(sa.String(120))),
    sa.Column('image_link', sa.String(length=500), nullable=True),
    sa.Column('facebook_link', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Venue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('city', sa.String(length=120), nullable=True),
    sa.Column('state', sa.String(length=120), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.Column('image_link', sa.String(length=500), nullable=True),
    sa.Column('genres', sa.ARRAY(sa.String(120))),
    sa.Column('facebook_link', sa.String(length=120), nullable=True),
    sa.Column('website_link', sa.String(length=120), nullable=True),
    sa.Column('seeking_talent', sa.Boolean(), nullable=True),
    sa.Column('seeking_description', sa.String(length=720), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Venue')
    op.drop_table('Artist')
    # ### end Alembic commands ###
