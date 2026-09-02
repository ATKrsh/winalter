"""
WinAlter CLI Compiler & Distribution Tool
"""

import os
import sys
import yaml
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from winalter.core.config import WinAlterSpec
from winalter.core.ast_compiler import WinAlterCompiler
from winalter.engine.build_pipeline import WinAlterBuildEngine
from winalter.presets.default_specs import PRESET_SPECS

console = Console()

def main():
    parser = argparse.ArgumentParser(description="WinAlter - Windows Image Engineering Platform CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Build command
    build_parser = subparsers.add_parser("build", help="Compile distribution specification into bootable ISO")
    build_parser.add_argument("spec_file", nargs="?", default="", help="Path to winalter.yaml distribution spec")
    build_parser.add_argument("--iso", required=True, help="Path to source Windows ISO")
    build_parser.add_argument("--index", type=int, default=1, help="WIM edition index (default: 1)")

    # Validate command
    val_parser = subparsers.add_parser("validate", help="Validate winalter.yaml specification and preview AST plan")
    val_parser.add_argument("spec_file", help="Path to winalter.yaml distribution spec")

    args = parser.parse_args()

    if args.command == "validate":
        if not os.path.exists(args.spec_file):
            console.print(f"[bold red]File not found: {args.spec_file}[/bold red]")
            return

        with open(args.spec_file, "r", encoding="utf-8") as f:
            spec = WinAlterSpec.from_yaml(f.read())

        compiler = WinAlterCompiler(spec)
        plan = compiler.compile()

        console.print(Panel.fit(f"[bold cyan]Validated Spec: {spec.meta.name} (v{spec.meta.version})[/bold cyan]", border_style="cyan"))
        
        table = Table(title="Compiled AST Execution Plan", border_style="magenta")
        table.add_column("Layer", style="bold white")
        table.add_column("Provider", style="cyan")
        table.add_column("Action", style="yellow")
        table.add_column("Risk Level", style="bold green")

        for layer_name, nodes in plan.layers.items():
            for node in nodes:
                table.add_row(
                    layer_name.split(":")[0],
                    node.provider,
                    node.action,
                    node.risk["level"].value
                )

        console.print(table)

    elif args.command == "build":
        if args.spec_file and os.path.exists(args.spec_file):
            with open(args.spec_file, "r", encoding="utf-8") as f:
                spec = WinAlterSpec.from_yaml(f.read())
        else:
            console.print("[yellow]No spec file provided. Using Stock Preset: Gaming & Performance.[/yellow]")
            spec = PRESET_SPECS["gaming"]

        def log_cb(msg):
            console.print(f"[dim]{msg}[/dim]")

        engine = WinAlterBuildEngine(workspace_root="project_workspace", output_dir="dist")
        output_iso = engine.execute_build(spec, args.iso, edition_index=args.index, log_callback=log_cb)
        console.print(f"\n[bold green]Success! Distribution ISO compiled: {output_iso}[/bold green]")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
