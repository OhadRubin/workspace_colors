# Color Picker

Python tools for applying VS Code workspace color themes.

## Installation

```bash
uv tool install .
```

This installs `colorpick` globally.

## Usage

### CLI

```bash
# List all themes
colorpick list

# Apply by theme name
colorpick apply -t forest

# Apply hex color directly
colorpick apply -c "#ff5500"

# Apply to specific workspace
colorpick apply -t sage -w /path/to/workspace
```

### TUI (interactive)

```bash
uv run python color_picker.py
```

Use arrow keys to browse, Enter to apply.

## Structure

```
color_picker/
├── base.py   # Core logic (no TUI deps) - use this for scripting
├── tui.py    # Textual TUI
├── cli.py    # CLI interface
```
