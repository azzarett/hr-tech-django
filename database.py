#!/usr/bin/env python3
"""Utility entrypoint for database administration tasks."""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

import django
from hrtech.conf import ENV_ID, ENV_POSSIBLE_OPTIONS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Utility helper for destructive DB actions: drop all tables, run"
            " migrations, and seed deterministic mock data."
        )
    )
    parser.add_argument(
        "command",
        choices=("reset", "database:reset"),
        help="Action to run. Use 'reset' to rebuild the database from scratch.",
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true",
        help="Only drop + migrate the database without inserting mock data.",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=0,
        choices=(0, 1, 2, 3),
        help="Verbosity level passed down to Django's migrate command.",
    )
    return parser.parse_args(argv)


def bootstrap_django() -> None:
    assert (
        ENV_ID in ENV_POSSIBLE_OPTIONS
    ), f"Set correct DJANGORLAR_ENV_ID env var. Possible options: {ENV_POSSIBLE_OPTIONS}"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"hrtech.env.{ENV_ID}")
    django.setup()


def drop_database(settings, connection) -> None:
    db_conf = settings.DATABASES["default"]
    engine = db_conf["ENGINE"]

    connection.close()

    if "sqlite" in engine:
        db_path = Path(db_conf["NAME"]).expanduser()
        if db_path.exists():
            db_path.unlink()
        return

    table_names = connection.introspection.table_names()
    if not table_names:
        return

    vendor = connection.vendor
    with connection.cursor() as cursor:
        if vendor == "mysql":
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            drop_tpl = "DROP TABLE IF EXISTS `{}`;"
        else:
            drop_tpl = 'DROP TABLE IF EXISTS "{}" CASCADE;'

        for table_name in table_names:
            cursor.execute(drop_tpl.format(table_name))

        if vendor == "mysql":
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")


def seed_mock_data(apps, transaction) -> None:
    User = apps.get_model("users", "User")
    Team = apps.get_model("teams", "Team")
    UserTeam = apps.get_model("teams", "UserTeam")
    Role = apps.get_model("teams", "Role")

    with transaction.atomic():
        users_payload = [
            {
                "email": "captain@example.com",
                "first_name": "Alice",
                "last_name": "Captain",
                "password": "captain123",
                "telegram_nick": "@alice",
            },
            {
                "email": "developer@example.com",
                "first_name": "Bob",
                "last_name": "Builder",
                "password": "builder123",
                "telegram_nick": "@bob",
            },
            {
                "email": "designer@example.com",
                "first_name": "Carol",
                "last_name": "Colors",
                "password": "designer123",
                "telegram_nick": "@carol",
            },
        ]

        users = [User.objects.create_user(**payload) for payload in users_payload]

        teams_payload = [
            {
                "name": "Dream Team",
                "educational_institution_type": "university",
                "city_id": uuid.uuid4(),
                "university_id": uuid.uuid4(),
            },
            {
                "name": "Rising Stars",
                "educational_institution_type": "college",
                "city_id": uuid.uuid4(),
                "university_id": None,
            },
        ]

        teams = [Team.objects.create(**payload) for payload in teams_payload]

        memberships = [
            {
                "user": users[0],
                "team": teams[0],
                "has_permission_manage_users": True,
                "has_permission_manage_projects": True,
            },
            {
                "user": users[1],
                "team": teams[0],
                "has_permission_manage_projects": True,
            },
            {
                "user": users[2],
                "team": teams[1],
            },
        ]

        for membership in memberships:
            UserTeam.objects.create(**membership)

        roles = [
            {"user": users[0], "team": teams[0], "role": "captain"},
            {"user": users[1], "team": teams[0], "role": "developer"},
            {"user": users[2], "team": teams[1], "role": "designer"},
        ]

        for role in roles:
            Role.objects.create(**role)


def reset_database(args) -> None:
    bootstrap_django()
    from django.apps import apps
    from django.conf import settings
    from django.core.management import call_command
    from django.db import connection, transaction

    print("Resetting database…")
    drop_database(settings, connection)
    print("Applying migrations…")
    call_command("migrate", interactive=False, verbosity=args.verbosity)

    if args.skip_seed:
        print("Skipping mock data seeding.")
        return

    print("Seeding mock data…")
    seed_mock_data(apps, transaction)
    print("Done.")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    if args.command in {"reset", "database:reset"}:
        reset_database(args)
    else:  # pragma: no cover - defensive future-proofing
        raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main(sys.argv[1:])
