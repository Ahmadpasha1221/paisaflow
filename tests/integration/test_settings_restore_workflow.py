"""Integration tests for the backup/restore workflow exposed through SettingsViewModel.

Covers the previously unreachable restore path and its shell-notification signals.
"""

from datetime import date
from pathlib import Path

import pytest

from paisaflow.application.services import AccountService, PersonService, TransactionService
from paisaflow.config.settings import settings
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from paisaflow.presentation.viewmodels.settings_viewmodel import SettingsViewModel


@pytest.fixture
def env(tmp_path: Path, monkeypatch):
    """Isolate the app data directory so backups never touch the developer's real data."""
    monkeypatch.setattr(settings, "base_data_dir", tmp_path)
    engine = create_db_engine(db_path=tmp_path / "live.db")
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))
    return tmp_path, engine, uow


def test_backup_is_listed_and_restore_replaces_data(env):
    _, engine, uow = env
    person = PersonService(uow).create_person(name="Restore Tester")
    acct = AccountService(uow).create_account(
        name="Wallet",
        account_type=AccountType.CASH,
        owner_person_id=person.id,
        opening_balance=Money(500000),
    )
    vm = SettingsViewModel(uow, engine)

    assert vm.backups == []  # nothing to restore on a fresh install

    backup_path = vm.createBackup()
    assert backup_path != ""
    backups = vm.backups
    assert len(backups) == 1
    assert backups[0]["path"] == backup_path
    assert backups[0]["name"].startswith("paisaflow_backup_")
    assert backups[0]["sizeText"].endswith("KB")

    # Mutate live data after the snapshot.
    with uow:
        cat = next(c for c in uow.categories.get_all() if c.name == "Groceries")
    TransactionService(uow).record_expense(
        transaction_date=date(2026, 10, 20),
        description="After snapshot",
        amount=Money(100000),
        account_id=acct.id,
        person_id=person.id,
        category_id=cat.id,
    )
    assert AccountService(uow).get_account_by_id(acct.id).balance_paise == 400000

    restored = []
    vm.databaseRestored.connect(lambda: restored.append(True))

    assert vm.restoreBackup(backup_path) is True
    assert restored == [True]  # the shell is told to refresh itself
    assert AccountService(uow).get_account_by_id(acct.id).balance_paise == 500000


def test_restore_reports_failure_for_missing_file(env):
    _, engine, uow = env
    vm = SettingsViewModel(uow, engine)

    errors = []
    vm.operationError.connect(errors.append)

    assert vm.restoreBackup(str(Path("does_not_exist.db"))) is False
    assert len(errors) == 1
    assert "does not exist" in errors[0]


def test_restore_rejects_incompatible_backup(env, tmp_path: Path):
    _, engine, uow = env
    vm = SettingsViewModel(uow, engine)

    bogus = tmp_path / "not_a_paisaflow_backup.db"
    bogus.write_bytes(b"this is not a sqlite database")

    errors = []
    vm.operationError.connect(errors.append)

    assert vm.restoreBackup(str(bogus)) is False
    assert len(errors) == 1
