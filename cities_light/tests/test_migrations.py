from __future__ import unicode_literals
import pytest
import io
from django import test
from django.apps import apps
from django.db.migrations.state import ProjectState
from django.db.migrations import Migration
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.questioner import (
    InteractiveMigrationQuestioner, MigrationQuestioner,
)
from django.db.migrations.autodetector import MigrationAutodetector


class TestNoMigrationLeft(test.TestCase):
    def test_no_migration_left(self):
        loader = MigrationLoader(None, ignore_no_migrations=True)
        conflicts = loader.detect_conflicts()
        app_labels = ['cities_light']

        autodetector = MigrationAutodetector(
            loader.project_state(),
            ProjectState.from_apps(apps),
            InteractiveMigrationQuestioner(specified_apps=app_labels, dry_run=True),
        )

        changes = autodetector.changes(
            graph=loader.graph,
            trim_to_apps=app_labels or None,
            convert_apps=app_labels or None,
        )

        assert 'cities_light' not in changes
