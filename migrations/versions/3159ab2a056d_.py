"""empty message

Revision ID: 3159ab2a056d
Revises: 6836ccae2ede
Create Date: 2022-10-23 16:57:30.604177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3159ab2a056d'
down_revision = '6836ccae2ede'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.user_id'], )
    )
    op.drop_table('follow')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follow',
    sa.Column('followed_id', sa.INTEGER(), nullable=False),
    sa.Column('follower_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['followed_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('followed_id', 'follower_id')
    )
    op.drop_table('followers')
    # ### end Alembic commands ###