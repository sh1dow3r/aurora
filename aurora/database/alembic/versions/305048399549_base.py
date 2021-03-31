"""Base

Revision ID: 305048399549
Revises: 
Create Date: 2021-03-15 19:04:04.143914

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "305048399549"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sample",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("filesize", sa.Integer(), nullable=False),
        sa.Column("filetype", sa.String(), nullable=False),
        sa.Column("md5", sa.String(length=32), nullable=False),
        sa.Column("sha1", sa.String(length=40), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("sha512", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sample_md5"), "sample", ["md5"], unique=False)
    op.create_index(op.f("ix_sample_sha1"), "sample", ["sha1"], unique=False)
    op.create_index(op.f("ix_sample_sha256"), "sample", ["sha256"], unique=True)
    op.create_index(op.f("ix_sample_sha512"), "sample", ["sha512"], unique=False)
    op.create_table(
        "minhash",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sample_id", sa.Integer(), nullable=True),
        sa.Column("seed", sa.BIGINT(), nullable=False),
        sa.Column("hash_values", sa.ARRAY(sa.BIGINT()), nullable=False),
        sa.Column(
            "minhash_type",
            sa.Enum("STRINGS_MINHASH", "DISASM_MINHASH", name="minhashtype"),
            nullable=False,
        ),
        sa.Column("extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(
            ["sample_id"],
            ["sample.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_minhash_minhash_type"), "minhash", ["minhash_type"], unique=False
    )
    op.create_table(
        "relation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("child_id", sa.Integer(), nullable=False),
        sa.Column(
            "relation_type",
            sa.Enum(
                "STRINGS_MINHASH",
                "DISASM_MINHASH",
                "STRING",
                "SSDEEP",
                name="relationtype",
            ),
            nullable=False,
        ),
        sa.Column(
            "confidence",
            sa.Float(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["child_id"],
            ["sample.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["sample.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_relation_parent_id"), "relation", ["parent_id"], unique=False
    )
    op.create_index(
        op.f("ix_relation_child_id"), "relation", ["child_id"], unique=False
    )
    op.create_table(
        "ssdeep",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sample_id", sa.Integer(), nullable=True),
        sa.Column("chunksize", sa.Integer(), nullable=False),
        sa.Column("ssdeep", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sample_id"],
            ["sample.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sample_id"),
    )
    op.create_table(
        "string",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sample_id", sa.Integer(), nullable=True),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("heuristic", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["sample_id"],
            ["sample.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_string_sha256"), "string", ["sha256"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_string_sha256"), table_name="string")
    op.drop_table("string")
    op.drop_table("ssdeep")
    op.drop_table("relation")
    op.drop_index(op.f("ix_minhash_minhash_type"), table_name="minhash")
    op.drop_table("minhash")
    op.drop_index(op.f("ix_sample_sha512"), table_name="sample")
    op.drop_index(op.f("ix_sample_sha256"), table_name="sample")
    op.drop_index(op.f("ix_sample_sha1"), table_name="sample")
    op.drop_index(op.f("ix_sample_md5"), table_name="sample")
    op.drop_table("sample")
    # ### end Alembic commands ###
