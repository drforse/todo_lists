"""init migrations

Revision ID: 7b0278a13b5b
Revises: 
Create Date: 2024-10-07 06:47:54.019746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7b0278a13b5b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password', postgresql.BYTEA(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'todo_lists',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'tasks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('todo_list_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('datetime_to_do', sa.DateTime(), nullable=False),
        sa.Column('info', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['todo_list_id'], ['todo_lists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('tasks')
    op.drop_table('todo_lists')
    op.drop_table('users')
