#!/usr/bin/env python

import argparse
import sys
import ctypes
from cleaner import DebugCleaner
try:
    from . debug import serve, cleanup, debugger, version
except:
    from debug import serve, cleanup, debugger, version

HANDLE = None

def handle_windows():
    global HANDLE
    if sys.platform == 'win32':
        HANDLE = ctypes.windll.user32.GetForegroundWindow()

def get_parser():
    parser = argparse.ArgumentParser(
        description="🔧 Debug Framework CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Subcommands')

    # === Subcommand: cleaner ===
    cleaner_parser = subparsers.add_parser(
        'cleaner',
        help='Manage debug statements in Python files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cleaner_args = DebugCleaner().usage()
    for action in cleaner_args._actions:
        if action.option_strings:
            cleaner_parser._add_action(action)
        elif action.dest != 'help':
            cleaner_parser._add_action(action)

    # === Subcommand: serve ===
    serve_parser = subparsers.add_parser('serve', help='Run debug message UDP server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    serve_parser.add_argument('--port', type=int, default=50001, help='Port to bind')
    serve_parser.add_argument('--on-top', action='store_true', help='Always On Top')
    serve_parser.add_argument('--center', action='store_true', help='Center the window')

    # === Subcommand: log ===
    log_parser = subparsers.add_parser('log', help='Database log inspection')
    log_parser.add_argument('--db-log', action='store_true', help='Show all logs')
    log_parser.add_argument('--db-log-tag', help='Filter log by tag')

    # === Subcommand: cleanup ===
    cleanup_parser = subparsers.add_parser('cleanup', help='Cleanup file')
    cleanup_parser.add_argument('path', help='Path file to clean')

    # === Subcommand: version ===
    subparsers.add_parser('version', help='Print version info')

    return parser


def main():
    handle_windows()
    parser = get_parser()

    if len(sys.argv) <= 1:
        parser.print_help()
        print("\n💡 Use 'debug.py <command> --help' for more details.")
        sys.exit(0)

    args = parser.parse_args()

    if args.command == 'cleaner':
        manager = DebugCleaner()
        python_files = manager.find_python_files(args.path)

        if not python_files:
            print("\u26a0\ufe0f No Python files found.")
            return

        action = 'clean'
        if getattr(args, 'comment_out', False):
            action = 'comment_out'
        elif getattr(args, 'comment_in', False):
            action = 'comment_in'

        results = []
        for file_path in python_files:
            result = manager.process_file(file_path, action, args.dry_run)
            results.append(result)

        manager.display_results(results, args.dry_run, action)

    elif args.command == 'serve':
        serve(args.host, args.port, args.on_top, args.center)

    elif args.command == 'log':
        if args.db_log:
            debugger.db_log()
        elif args.db_log_tag:
            debugger.db_log(args.db_log_tag)

    elif args.command == 'cleanup':
        cleanup(args.path)

    elif args.command == 'version':
        print("VERSION:", version())


if __name__ == '__main__':
    main()
