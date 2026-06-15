#!/usr/bin/env python3

"""Top-level subcommand CLI for the devops-manual tools."""

import importlib
import os
import sys
from dataclasses import dataclass
from typing import Callable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.expanduser("~/devops/devops-manual/opskit"))


@dataclass(frozen=True)
class Command:
    """A lazily imported command module."""

    modules: tuple[str, ...]
    help: str


COMMANDS = {
    "alert": Command(("alert",), "Send email and webhook alerts"),
    "audit": Command(("audit",), "Inspect local system health"),
    "deploy": Command(("deploy",), "Deploy code and restart a service"),
    "inventory": Command(("inventory",), "Scan hosts and export inventory"),
    "logs": Command(("logs",), "Fetch, filter, count, or stream logs"),
    "net": Command(("net",), "Run network diagnostics"),
    "report": Command(("opskit.report", "report"), "Generate HTML or JSON system reports"),
    "watch": Command(("watch",), "Watch and manage a systemd service"),
}


def _module_main(module_names: tuple[str, ...]) -> Callable[[], object]:
    last_error = None
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as exc:
            last_error = exc
            continue

        main = getattr(module, "main", None)
        if main is None:
            raise SystemExit(f"Command module '{module_name}' does not define main().")
        return main

    names = ", ".join(module_names)
    raise SystemExit(f"Could not import command module. Tried: {names}") from last_error


def _run_command(command_name: str, command_args: list[str]) -> object:
    command = COMMANDS[command_name]
    main = _module_main(command.modules)

    # Most existing command modules parse sys.argv directly. Keep their parser
    # behavior intact while presenting one git-style top-level executable.
    previous_argv = sys.argv
    sys.argv = [f"{previous_argv[0]} {command_name}", *command_args]
    try:
        try:
            return main(command_args)
        except TypeError:
            return main()
    finally:
        sys.argv = previous_argv


def build_parser():
    import argparse

    parser = argparse.ArgumentParser(
        prog="devops-manual",
        description="DevOps manual command-line toolkit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="devops-manual 1.0.0",
    )

    subparsers = parser.add_subparsers(metavar="<command>")

    for name, command in sorted(COMMANDS.items()):
        subparser = subparsers.add_parser(
            name,
            help=command.help,
            description=command.help,
            add_help=False,
        )

    return parser


def main(argv: list[str] | None = None) -> object:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    if not argv:
        parser.print_help()
        return 2

    if argv[0] in {"-h", "--help"}:
        parser.parse_args(argv)
        return 0

    if argv[0] in {"-V", "--version"}:
        parser.parse_args(argv)
        return 0

    command_name = argv[0]
    if command_name not in COMMANDS:
        parser.error(f"unknown command: {command_name}")

    return _run_command(command_name, argv[1:])


if __name__ == "__main__":
    sys.exit(main())
