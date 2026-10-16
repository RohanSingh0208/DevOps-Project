"""Alembic environment configuration."""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models so Alembic can detect them for autogenerate
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base  # noqa: E402
from app.models import Resource, Reservation, MaintenanceRequest  # noqa: F401,E402

target_metadata = Base.metadata

# Override sqlalchemy.url from env variable
database_url_sync = os.environ.get("DATABASE_URL_SYNC")
if not database_url_sync:
    db_url = os.environ.get("DATABASE_URL", "")
    if "asyncpg" in db_url:
        database_url_sync = db_url.replace("+asyncpg", "+psycopg2")
    elif db_url:
        database_url_sync = db_url
    else:
        database_url_sync = "postgresql+psycopg2://campus_admin:changeme@localhost:5432/campus_resource_hub"
config.set_main_option("sqlalchemy.url", database_url_sync)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (uses live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
