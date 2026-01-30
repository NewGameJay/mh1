"""
Structured Input Collection for MH1

Handles [[INPUT:name]] markers and collects structured data from users.
"""

from pathlib import Path
from typing import Any, Optional
import yaml

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Brand colors
C = {
    "pink": "#EC4899",
    "rose": "#F472B6",
    "orange": "#F97316",
    "amber": "#FBBF24",
    "yellow": "#FDE047",
    "white": "#FAFAFA",
    "gray": "#9CA3AF",
    "dim": "#4B5563",
    "green": "#22C55E",
    "red": "#EF4444",
    "cyan": "#06B6D4",
}

console = Console()

# Cache for loaded schemas
_schemas_cache: Optional[dict] = None


def load_input_schemas(config_path: Optional[Path] = None) -> dict:
    """Load input schemas from YAML config."""
    global _schemas_cache

    if _schemas_cache is not None:
        return _schemas_cache

    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "input_schemas.yaml"

    if config_path.exists():
        with open(config_path) as f:
            _schemas_cache = yaml.safe_load(f)
    else:
        _schemas_cache = {}

    return _schemas_cache


class InputCollector:
    """Collects structured input based on schemas."""

    def __init__(self):
        self.schemas = load_input_schemas()

    def collect(self, schema_name: str, prefill: Optional[dict] = None) -> dict:
        """
        Collect input for a named schema.

        Args:
            schema_name: Name of the schema (e.g., "onboarding_basics")
            prefill: Optional dict of pre-filled values

        Returns:
            Dict of collected values
        """
        schema = self.schemas.get(schema_name)
        if not schema:
            console.print(f"[{C['red']}]Unknown input schema: {schema_name}[/]")
            return {}

        prefill = prefill or {}
        results = {}

        # Show header
        title = schema.get("title", schema_name)
        description = schema.get("description", "")

        console.print()
        console.print(Panel(
            f"[{C['white']}]{description}[/]",
            title=f"[bold {C['pink']}]{title}[/]",
            border_style=C['pink']
        ))
        console.print()

        # Handle confirmation type
        if schema.get("type") == "confirmation":
            return self._collect_confirmation(schema)

        # Collect each field
        fields = schema.get("fields", [])
        for field in fields:
            name = field["name"]
            field_type = field.get("type", "text")

            # Skip if prefilled
            if name in prefill:
                results[name] = prefill[name]
                console.print(f"  [{C['dim']}]{field['prompt']}:[/] [{C['green']}]{prefill[name]}[/] (prefilled)")
                continue

            # Collect based on type
            if field_type == "text":
                results[name] = self._collect_text(field)
            elif field_type == "url":
                results[name] = self._collect_url(field)
            elif field_type == "select":
                results[name] = self._collect_select(field)
            elif field_type == "multiselect":
                results[name] = self._collect_multiselect(field)
            elif field_type == "number":
                results[name] = self._collect_number(field)
            elif field_type == "boolean":
                results[name] = self._collect_boolean(field)

        console.print()
        return results

    def _collect_text(self, field: dict) -> str:
        """Collect text input."""
        prompt = field.get("prompt", field["name"])
        required = field.get("required", False)
        placeholder = field.get("placeholder", "")

        hint = f" [{C['dim']}]({placeholder})[/]" if placeholder else ""
        req_marker = f"[{C['red']}]*[/]" if required else ""

        while True:
            value = console.input(f"  [{C['white']}]{prompt}{req_marker}[/]{hint}: ").strip()

            if not value and required:
                console.print(f"    [{C['red']}]This field is required[/]")
                continue

            return value

    def _collect_url(self, field: dict) -> str:
        """Collect URL input."""
        prompt = field.get("prompt", field["name"])
        required = field.get("required", False)
        placeholder = field.get("placeholder", "https://")

        hint = f" [{C['dim']}]({placeholder})[/]" if placeholder else ""
        req_marker = f"[{C['red']}]*[/]" if required else ""

        while True:
            value = console.input(f"  [{C['white']}]{prompt}{req_marker}[/]{hint}: ").strip()

            if not value:
                if required:
                    console.print(f"    [{C['red']}]This field is required[/]")
                    continue
                return ""

            # Basic URL validation
            if not value.startswith(("http://", "https://")):
                value = "https://" + value

            return value

    def _collect_select(self, field: dict) -> str:
        """Collect single selection from options."""
        prompt = field.get("prompt", field["name"])
        options = field.get("options", [])
        required = field.get("required", False)

        req_marker = f"[{C['red']}]*[/]" if required else ""
        console.print(f"  [{C['white']}]{prompt}{req_marker}[/]")

        for i, opt in enumerate(options, 1):
            console.print(f"    [{C['yellow']}]{i}[/]. [{C['gray']}]{opt}[/]")

        while True:
            choice = console.input(f"    [{C['pink']}]>[/] ").strip()

            # Allow typing the option directly
            if choice in options:
                return choice

            # Allow numeric selection
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    console.print(f"    [{C['green']}]→ {options[idx]}[/]")
                    return options[idx]

            if not choice and not required:
                return ""

            console.print(f"    [{C['red']}]Please enter a number 1-{len(options)} or type an option[/]")

    def _collect_multiselect(self, field: dict) -> list:
        """Collect multiple selections from options."""
        prompt = field.get("prompt", field["name"])
        options = field.get("options", [])
        required = field.get("required", False)

        req_marker = f"[{C['red']}]*[/]" if required else ""
        console.print(f"  [{C['white']}]{prompt}{req_marker}[/] [{C['dim']}](comma-separated numbers)[/]")

        for i, opt in enumerate(options, 1):
            console.print(f"    [{C['yellow']}]{i}[/]. [{C['gray']}]{opt}[/]")

        while True:
            choice = console.input(f"    [{C['pink']}]>[/] ").strip()

            if not choice:
                if required:
                    console.print(f"    [{C['red']}]Please select at least one option[/]")
                    continue
                return []

            # Parse comma-separated numbers
            selected = []
            parts = [p.strip() for p in choice.split(",")]

            valid = True
            for part in parts:
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(options):
                        selected.append(options[idx])
                    else:
                        valid = False
                        break
                elif part in options:
                    selected.append(part)
                else:
                    valid = False
                    break

            if valid and selected:
                console.print(f"    [{C['green']}]→ {', '.join(selected)}[/]")
                return selected

            console.print(f"    [{C['red']}]Please enter valid numbers separated by commas[/]")

    def _collect_number(self, field: dict) -> Optional[int]:
        """Collect numeric input."""
        prompt = field.get("prompt", field["name"])
        required = field.get("required", False)
        min_val = field.get("min")
        max_val = field.get("max")

        req_marker = f"[{C['red']}]*[/]" if required else ""

        while True:
            value = console.input(f"  [{C['white']}]{prompt}{req_marker}[/]: ").strip()

            if not value:
                if required:
                    console.print(f"    [{C['red']}]This field is required[/]")
                    continue
                return None

            try:
                num = int(value)
                if min_val is not None and num < min_val:
                    console.print(f"    [{C['red']}]Must be at least {min_val}[/]")
                    continue
                if max_val is not None and num > max_val:
                    console.print(f"    [{C['red']}]Must be at most {max_val}[/]")
                    continue
                return num
            except ValueError:
                console.print(f"    [{C['red']}]Please enter a number[/]")

    def _collect_boolean(self, field: dict) -> bool:
        """Collect yes/no input."""
        prompt = field.get("prompt", field["name"])
        default = field.get("default", False)

        default_hint = "Y/n" if default else "y/N"
        value = console.input(f"  [{C['white']}]{prompt}[/] [{C['dim']}]({default_hint})[/]: ").strip().lower()

        if not value:
            return default
        return value in ("y", "yes", "true", "1")

    def _collect_confirmation(self, schema: dict) -> dict:
        """Collect confirmation choice."""
        options = schema.get("options", [])

        for opt in options:
            key = opt["key"]
            label = opt["label"]
            console.print(f"  [{C['yellow']}][{key.upper()}][/] [{C['white']}]{label}[/]")

        console.print()
        choice = console.input(f"  [{C['pink']}]>[/] ").strip().lower()

        for opt in options:
            if choice == opt["key"]:
                return {"choice": opt["action"]}

        # Default to first option
        return {"choice": options[0]["action"]}


def show_confirmation(message: str, options: Optional[list] = None) -> str:
    """
    Show a confirmation dialog.

    Args:
        message: The message to display
        options: Optional list of options (defaults to Yes/No/Edit)

    Returns:
        The selected action
    """
    if options is None:
        options = [
            {"key": "y", "label": "Yes, proceed", "action": "YES"},
            {"key": "n", "label": "No, let me modify", "action": "NO"},
            {"key": "e", "label": "Edit files directly", "action": "EDIT"},
        ]

    console.print()
    console.print(Panel(
        message,
        title=f"[bold {C['amber']}]Confirm[/]",
        border_style=C['amber']
    ))
    console.print()

    for opt in options:
        key = opt["key"]
        label = opt["label"]
        console.print(f"  [{C['yellow']}][{key.upper()}][/] [{C['white']}]{label}[/]")

    console.print()
    choice = console.input(f"  [{C['pink']}]>[/] ").strip().lower()

    for opt in options:
        if choice == opt["key"]:
            return opt["action"]

    # Default to NO if unrecognized
    return "NO"


def format_collected_inputs(inputs: dict) -> str:
    """Format collected inputs as a nice summary."""
    lines = []
    for key, value in inputs.items():
        if isinstance(value, list):
            value = ", ".join(value)
        display_key = key.replace("_", " ").title()
        lines.append(f"• {display_key}: {value}")
    return "\n".join(lines)
