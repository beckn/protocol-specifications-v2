# GUI Installation Instructions

## Missing Dependency: tkinter

The Python GUI requires `tkinter` which is not currently installed on your system.

## Installation

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

### Fedora/RHEL
```bash
sudo dnf install python3-tkinter
```

### macOS (with Homebrew)
```bash
# tkinter should be included with Python
# If not, reinstall Python:
brew reinstall python@3
```

### Verify Installation
```bash
python3 -c "import tkinter; print('tkinter installed successfully')"
```

## Running the GUI

Once tkinter is installed:

```bash
cd /home/ravi/www/protocol-specifications-v2
python3 scripts/v2.1/v2_to_v21_converter/transformerGUI.py
```

## Alternative: Command-Line Interface

If you prefer not to install tkinter, use the CLI version:

```bash
# Transform with version
python3 scripts/v2.1/v2_to_v21_converter/becknVersionTransform.py \
  -ov 2.1 \
  -i input.json \
  -o output.json

# Transform with custom files
python3 scripts/v2.1/v2_to_v21_converter/becknVersionTransform.py \
  --context-file schema/core/v2.1/updated.context.jsonld \
  --vocab-file schema/core/v2.1/updated.vocab.jsonld \
  --attributes-file schema/core/v2.1/attributes.yaml \
  -i input.json \
  -o output.json
```

## Features Available

### GUI (transformerGUI.py)
- ✅ Dual-pane JSON viewer
- ✅ File upload interface
- ✅ Real-time transformation
- ✅ Copy/Save output
- ✅ Visual progress indicator
- ✅ Warning display

### CLI (becknVersionTransform.py)
- ✅ Batch processing
- ✅ Scriptable
- ✅ Pipe-friendly
- ✅ All transformation features

Both use the same pure IRI-based transformation engine!
