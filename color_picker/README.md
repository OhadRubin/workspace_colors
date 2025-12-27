# Color Picker

Python tools for applying VS Code workspace color themes.

## Usage

### TUI (interactive)

```bash
python color_picker.py
```

Use arrow keys to browse, Enter to apply.

### CLI

```bash
# List all themes
python -m color_picker list

# Apply by theme name
python -m color_picker apply -t forest

# Apply hex color directly
python -m color_picker apply -c "#ff5500"

# Apply to specific workspace
python -m color_picker apply -t sage -w /path/to/workspace
```

## Structure

```
color_picker/
├── base.py   # Core logic (no TUI deps) - use this for scripting
├── tui.py    # Textual TUI
├── cli.py    # CLI interface
```
