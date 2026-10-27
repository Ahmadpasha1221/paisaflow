"""Database migration and initialization manager."""

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from paisaflow.domain.entities.category import DEFAULT_EXPENSE_CATEGORIES, DEFAULT_INCOME_CATEGORIES
from paisaflow.infrastructure.database.engine import Base
from paisaflow.infrastructure.database.models import AppSettingModel, CategoryModel


def initialize_database(engine: Engine) -> None:
    """Create tables if not existing, seed default categories and system settings."""
    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        # Check if default categories exist
        cat_count = session.scalar(select(CategoryModel.id).limit(1))
        if cat_count is None:
            # Seed income categories
            for name, icon, color in DEFAULT_INCOME_CATEGORIES:
                session.add(
                    CategoryModel(
                        name=name,
                        category_type="income",
                        icon_name=icon,
                        color_code=color,
                    )
                )

            # Seed expense categories
            for name, icon, color in DEFAULT_EXPENSE_CATEGORIES:
                session.add(
                    CategoryModel(
                        name=name,
                        category_type="expense",
                        icon_name=icon,
                        color_code=color,
                    )
                )

        # Seed initial app settings if not set
        default_settings = {
            "theme": "dark",
            "currency": "INR",
            "locale": "en_IN",
            "first_day_of_week": "monday",
            "backup_retention_days": "30",
            "onboarding_completed": "false",
        }
        for k, v in default_settings.items():
            existing = session.get(AppSettingModel, k)
            if not existing:
                session.add(AppSettingModel(key=k, value=v))

        session.commit()
