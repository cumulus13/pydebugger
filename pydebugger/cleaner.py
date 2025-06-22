#!/usr/bin/env python3
"""
Debug Line Manager - Scripts to manage debug statements in python files
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

try:
    from .custom_rich_help_formatter import CustomRichHelpFormatter
except:
    from custom_rich_help_formatter import CustomRichHelpFormatter

console = Console()

class DebugCleaner:
    def __init__(self):
        # Improved regex pattern - more flexible
        self.debug_pattern = re.compile(
            r'(\s*)(#\s*)?debug\s*\(\s*exchange_name\s*=\s*exchange_name\s*(?:,\s*debug\s*=\s*1)?\s*(?:,\s*)?\)',
            re.IGNORECASE
        )
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'lines_changed': 0,
            'errors': 0
        }
    
    def find_python_files(self, path: str) -> List[Path]:
        """Looking for all python files (.py dan .pyw) In a single directory or file"""
        python_files = []
        path_obj = Path(path)
        
        if path_obj.is_file():
            # Jika input adalah file tunggal
            if path_obj.suffix in ('.py', '.pyw'):
                python_files.append(path_obj)
            else:
                console.print(f"[bold yellow]⚠️ File '{path}' Not a python file (.py/.pyw)[/bold yellow]")
        elif path_obj.is_dir():
            # Jika input adalah direktori
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.pyw')):
                        python_files.append(Path(root) / file)
        else:
            console.print(f"[bold red]❌ Path '{path}' not found[/bold red]")
        
        return python_files
    
    def process_line1(self, line: str, action: str) -> Tuple[str, bool]:
        """
        Processing one line based on the requested action
        Returns: (processed_line, was_changed)
        """
        match = self.debug_pattern.search(line)
        if not match:
            return line, False
        
        indent = match.group(1)
        is_commented = match.group(2) is not None
        
        # if action == 'clean':
        #     # Delete Debug Parameters = 1 and clean up trailing commas
        #     new_line = re.sub(
        #         r'debug\s*\(\s*exchange_name\s*=\s*exchange_name\s*,\s*debug\s*=\s*1\s*(?:,\s*)?\)',
        #         'debug(exchange_name = exchange_name)',
        #         line,
        #         flags=re.IGNORECASE
        #     )
        #     # Also handle case without debug=1 but with trailing comma
        #     if new_line == line:
        #         new_line = re.sub(
        #             r'debug\s*\(\s*exchange_name\s*=\s*exchange_name\s*,\s*\)',
        #             'debug(exchange_name = exchange_name)',
        #             line,
        #             flags=re.IGNORECASE
        #         )
        #     return new_line, new_line != line
        
        if action == 'clean':
            # Remove Debug = 1 of all debug calls ()
            new_line = re.sub(
                r'(debug\s*\([^)]*?),\s*debug\s*=\s*1\s*(?=[,)])',
                r'\1',
                line
            )
            # Hapus trailing koma sebelum tanda tutup kurung jika perlu
            new_line = re.sub(r',\s*\)', ')', new_line)
            return new_line, new_line != line

        
        elif action == 'comment_out':
            if not is_commented:
                # Add comments
                new_line = re.sub(
                    r'(\s*)(debug\s*\(.*?\))',
                    r'\1#\2',
                    line,
                    flags=re.IGNORECASE
                )
                return new_line, True
            return line, False
        
        elif action == 'comment_in':
            if is_commented:
                # Delete comments
                new_line = re.sub(
                    r'(\s*)#\s*(debug\s*\(.*?\))',
                    r'\1\2',
                    line,
                    flags=re.IGNORECASE
                )
                return new_line, True
            return line, False
        
        return line, False
    
    def process_line(self, line: str, action: str) -> Tuple[str, bool]:
        """
        Process one line based on the requested action
        Returns: (processed_line, was_changed)
        """
        if action == 'clean':
            # Bersihkan debug=1 dari semua debug(...) calls
            new_line = re.sub(
                r'(debug\s*\([^)]*?),\s*debug\s*=\s*1\s*(?=[,)])',
                r'\1',
                line
            )
            new_line = re.sub(r',\s*\)', ')', new_line)
            return new_line, new_line != line

        elif action == 'comment_out':
            # Komentari semua baris debug(...) yang belum dikomentari
            if re.search(r'^\s*debug\s*\(.*?\)', line, flags=re.IGNORECASE):
                new_line = re.sub(
                    r'^(\s*)(debug\s*\(.*?\))',
                    r'\1#\2',
                    line,
                    flags=re.IGNORECASE
                )
                return new_line, True
            return line, False

        elif action == 'comment_in':
            # Hapus tanda komentar dari debug(...) yang dikomentari
            if re.search(r'^\s*#\s*debug\s*\(.*?\)', line, flags=re.IGNORECASE):
                new_line = re.sub(
                    r'^(\s*)#\s*(debug\s*\(.*?\))',
                    r'\1\2',
                    line,
                    flags=re.IGNORECASE
                )
                return new_line, True
            return line, False

        return line, False

    def process_file(self, file_path: Path, action: str, dry_run: bool = False) -> Dict:
        """Process one file"""
        result = {
            'file': file_path,
            'changes': [],
            'error': None,
            'modified': False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            for line_num, line in enumerate(lines, 1):
                new_line, changed = self.process_line(line, action)
                new_lines.append(new_line)
                
                if changed:
                    result['changes'].append({
                        'line_num': line_num,
                        'old': line.rstrip(),
                        'new': new_line.rstrip()
                    })
                    result['modified'] = True
            
            # Write a file if there is a change and not dry run
            if result['modified'] and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
            
            if result['modified']:
                self.stats['lines_changed'] += len(result['changes'])
                self.stats['files_modified'] += 1
            
        except Exception as e:
            result['error'] = str(e)
            self.stats['errors'] += 1
        
        self.stats['files_processed'] += 1
        return result
    
    def display_results(self, results: List[Dict], dry_run: bool, action: str):
        """Showing processing results"""
        
        # Header
        action_icons = {
            'clean': '🔧',
            'comment_out': '💬',
            'comment_in': '🔓'
        }
        
        action_names = {
            'clean': 'Clean Debug Parameters',
            'comment_out': 'Comment Out Debug Lines',
            'comment_in': 'Uncomment Debug Lines'
        }
        
        icon = action_icons.get(action, '⚙️')
        action_name = action_names.get(action, action.replace('_', ' ').title())
        
        mode = "[bold red]DRY RUN[/bold red]" if dry_run else "[bold green]EXECUTION[/bold green]"
        
        console.print(Panel(
            f"{icon} {action_name} - {mode}",
            title="Debug Manager Results",
            title_align="center",
            border_style="blue"
        ))
        
        # Summary table
        summary_table = Table(title="📊 Summary Statistics")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="magenta", justify="right")
        
        summary_table.add_row("Files Processed", str(self.stats['files_processed']))
        summary_table.add_row("Files Modified", str(self.stats['files_modified']))
        summary_table.add_row("Lines Changed", str(self.stats['lines_changed']))
        summary_table.add_row("Errors", str(self.stats['errors']))
        
        console.print(summary_table)
        console.print()
        
        # Details of change
        if any(result['modified'] for result in results):
            console.print("[bold green]📝 Files with Changes:[/bold green]")
            
            for result in results:
                if result['modified']:
                    console.print(f"\n[bold blue]📄 {result['file']}[/bold blue]")
                    
                    for change in result['changes']:
                        console.print(f"  [yellow]Line {change['line_num']}:[/yellow]")
                        console.print(f"    [red]- {change['old']}[/red]")
                        console.print(f"    [green]+ {change['new']}[/green]")
        
        # Errors
        if any(result['error'] for result in results):
            console.print("\n[bold red]❌ Errors:[/bold red]")
            for result in results:
                if result['error']:
                    console.print(f"  [bold red]✗[/bold red] {result['file']}: {result['error']}")
                    
    def usage(self):
        parser = argparse.ArgumentParser(
        description="🐍 Debug Line Manager - Manage debug statements in Python files",
        formatter_class=CustomRichHelpFormatter,
        epilog="""[bold yellow]Examples of use:[/bold yellow]
    [cyan]%(prog)s[/cyan] [green]/path/to/project[/green]                    [dim]# Clean debug parameters from directory[/dim] | 
    [cyan]%(prog)s[/cyan] [green]/path/to/file.py[/green]                    [dim]# Clean debug parameters from single file[/dim] | 
    [cyan]%(prog)s[/cyan] [green]/path/to/project[/green] [yellow]--dry-run[/yellow]          [dim]# Preview changes without modifying files[/dim] | 
    [cyan]%(prog)s[/cyan] [green]/path/to/file.py[/green] [yellow]-co[/yellow]                [dim]# Comment out debug lines in file[/dim] | 
    [cyan]%(prog)s[/cyan] [green]/path/to/project[/green] [yellow]-ci[/yellow]                [dim]# Uncomment debug lines in directory[/dim]
            """
        )
        
        parser.add_argument(
            'path',
            help='📁 Path to directory or Python file for processing'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='👁️ Preview changes without modifying files'
        )
        
        action_group = parser.add_mutually_exclusive_group()
        action_group.add_argument(
            '-co', '--comment-out',
            action='store_true',
            help='💬 Comment out debug lines (add # in front)'
        )
        
        action_group.add_argument(
            '-ci', '--comment-in',
            action='store_true',
            help='🔓 Uncomment debug lines (remove # in front)'
        )
        
        return parser
    
def main():
    parser = DebugCleaner().usage()
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return 
    
    args = parser.parse_args()
    
    # Path validation
    if not os.path.exists(args.path):
        console.print(f"[bold red]❌ Error: '{args.path}' not found[/bold red]")
        sys.exit(1)
    
    # Determine action - FIXED: consistent naming
    if args.comment_out:
        action = 'comment_out'
    elif args.comment_in:
        action = 'comment_in'
    else:
        action = 'clean'  # ✅ Now consistent with process_line()
    
    # Initialize manager
    manager = DebugCleaner()
    
    # Find Python files
    path_type = "file" if os.path.isfile(args.path) else "directory"
    console.print(f"[bold blue]🔍 Looking for Python files in {path_type}: {args.path}[/bold blue]")
    python_files = manager.find_python_files(args.path)
    
    if not python_files:
        console.print("[bold yellow]⚠️ No Python files (.py/.pyw) found[/bold yellow]")
        sys.exit(0)
    
    console.print(f"[bold green]✅ Found {len(python_files)} Python file(s)[/bold green]")
    
    # Process files with progress bar
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Processing files...", total=len(python_files))
        
        for file_path in python_files:
            progress.update(task, description=f"Processing {file_path.name}")
            result = manager.process_file(file_path, action, args.dry_run)
            results.append(result)
            progress.advance(task)
    
    # Display results
    manager.display_results(results, args.dry_run, action)
    
    # Final message
    if args.dry_run:
        console.print(f"\n[bold blue]ℹ️ This is a dry run. Use without '--dry-run' to apply changes.[/bold blue]")
    elif manager.stats['files_modified'] > 0:
        console.print(f"\n[bold green]✅ Done! {manager.stats['files_modified']} file(s) successfully modified.[/bold green]")
    else:
        console.print(f"\n[bold yellow]ℹ️ No changes needed.[/bold yellow]")
        
    return parser

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ Operation canceled by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]")
        sys.exit(1)