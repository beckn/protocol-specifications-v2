# Beckn Protocol Version Transformer - GUI Application

A graphical user interface for transforming Beckn protocol JSON files between versions using pure IRI-based transformation.

## Features

### 🎨 Dual-Pane Interface
- **Left Pane**: Input JSON viewer
- **Right Pane**: Output JSON viewer
- Real-time transformation visualization

### 📁 File Management
- Upload input JSON files
- Upload custom ontology files:
  - `context.jsonld` - IRI to keyword mappings
  - `vocab.jsonld` - Ontology relationships
  - `attributes.yaml` - Schema definitions
- Save transformed output
- Copy output to clipboard

### ⚙️ Configuration Options
- Strip namespace prefixes (beckn:, schema:)
- Specify output version
- Use custom ontology files OR version-based transformation

### 📊 Status & Feedback
- Real-time status updates
- Progress indicator during transformation
- Warning display for potential issues
- Transformation statistics

## Installation

### Prerequisites
```bash
# Python 3.8+ required
python3 --version

# Install dependencies
pip install pyyaml
```

### Launch GUI
```bash
cd /home/ravi/www/protocol-specifications-v2

# Run the GUI
python3 scripts/v2.1/v2_to_v21_converter/transformerGUI.py
```

## Usage

### Basic Workflow

1. **Upload Input JSON**
   - Click "Browse..." next to "Input JSON"
   - Select your v2.0 JSON file
   - JSON displays in left pane

2. **Choose Transformation Mode**

   **Option A: Version-Based (Simple)**
   - Leave ontology files empty
   - Set "Output Version" (e.g., 2.1)
   - Click "Transform"

   **Option B: Custom Files (Advanced)**
   - Upload context.jsonld
   - Upload vocab.jsonld
   - Upload attributes.yaml
   - Click "Transform"

3. **View Results**
   - Transformed JSON displays in right pane
   - Check status bar for warnings
   - Copy or save output

### Screenshots & Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Beckn Protocol Version Transformer                              │
├─────────────────────────────────────────────────────────────────┤
│  Configuration                                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Input JSON:        [filename.json]          [Browse...]  │ │
│  │  ───────────────────────────────────────────────────────  │ │
│  │  Context File:      [context.jsonld]         [Browse...]  │ │
│  │  Vocab File:        [vocab.jsonld]           [Browse...]  │ │
│  │  Attributes File:   [attributes.yaml]        [Browse...]  │ │
│  │  ───────────────────────────────────────────────────────  │ │
│  │  ☑ Strip prefixes    Output Version: [2.1]               │ │
│  │              [🔄 Transform]  [Clear All]                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐ │
│  │  Input JSON             │  │  Output JSON                 │ │
│  │  ─────────────────────  │  │  ──────────────────────────  │ │
│  │  {                      │  │  {                           │ │
│  │    "@context": "...",   │  │    "@context": "...",        │ │
│  │    "context": {         │  │    "context": {              │ │
│  │      "version": "2.0",  │  │      "version": "2.0",       │ │
│  │      ...                │  │      ...                     │ │
│  │    }                    │  │    }                         │ │
│  │  }                      │  │  }                           │ │
│  │                         │  │                              │ │
│  │                         │  │           [Copy]  [Save...]  │ │
│  └─────────────────────────┘  └─────────────────────────────┘ │
│                                                                  │
│  Status: Ready                                          [====]  │
└─────────────────────────────────────────────────────────────────┘
```

## Features in Detail

### Smart File Handling
- Automatically formats JSON with proper indentation
- Validates JSON syntax on load
- Shows friendly file names in UI

### Error Handling
- Clear error messages for invalid files
- Validation of required files
- Graceful handling of transformation errors

### Performance
- Non-blocking UI during transformation
- Progress indicator for long operations
- Responsive interface

### Output Options
- **Copy**: Copy transformed JSON to clipboard
- **Save**: Save to file with dialog
- **Clear**: Reset all fields

## Keyboard Shortcuts

- `Ctrl+O`: Open input JSON (when focus on input pane)
- `Ctrl+S`: Save output (when focus on output pane)
- `Ctrl+C`: Copy selected text

## Example Use Cases

### 1. Quick Version Upgrade
```
1. Upload v2.0 JSON
2. Set version to "2.1"
3. Click Transform
4. Save output
```

### 2. Custom Ontology Testing
```
1. Upload test JSON
2. Upload experimental context.jsonld
3. Upload experimental vocab.jsonld
4. Upload test attributes.yaml
5. Click Transform
6. Review output and warnings
```

### 3. Batch Validation
```
1. Upload JSON file 1
2. Transform
3. Review warnings
4. Save if good
5. Clear all
6. Repeat for next file
```

## Troubleshooting

### "Missing Files" Error
- Ensure all three ontology files are uploaded when using custom mode
- OR clear all ontology files and use version-based mode

### "Failed to load JSON" Error
- Check JSON syntax is valid
- Ensure file encoding is UTF-8
- Verify file is not corrupted

### No Output Displayed
- Check status bar for error messages
- Review transformation warnings dialog
- Verify input JSON is valid Beckn format

### GUI Not Responding
- Wait for progress bar to complete
- Large files may take longer
- Check console for error messages

## Technical Details

### Architecture
```
transformerGUI.py
    ↓
becknVersionTransform.py (IRITransformer)
    ↓
├─ context.jsonld    (IRI mappings)
├─ vocab.jsonld      (Ontology relationships)
└─ attributes.yaml   (Schema definitions)
```

### Dependencies
- **tkinter**: GUI framework (built-in)
- **json**: JSON parsing (built-in)
- **yaml**: YAML parsing (pip install)
- **pathlib**: Path handling (built-in)

### Performance
- Typical transformation: < 1 second
- Large files (>1MB): 2-5 seconds
- UI remains responsive throughout

## Advanced Features

### Custom Styling
The GUI automatically selects the best available theme for your system.

### Status Messages
- **Ready**: Waiting for input
- **Loaded**: File successfully loaded
- **Transforming...**: Processing in progress
- **✓ Transformation complete**: Success
- **Error**: Check message for details

### Warning Display
- Warnings shown in popup dialog
- First 10 warnings displayed
- Count of additional warnings provided

## Integration

### Command-Line Alternative
If you prefer CLI, use:
```bash
python3 becknVersionTransform.py -ov 2.1 -i input.json -o output.json
```

### Batch Processing
For multiple files, use shell scripts:
```bash
for file in *.json; do
    python3 becknVersionTransform.py -ov 2.1 -i "$file" -o "v2.1_$file"
done
```

## Support

For issues or questions:
- Check `IRI_TRANSFORMER_GUIDE.md` for algorithm details
- Review `USAGE.md` for CLI reference
- See `IRI_RESOLUTION_ALGORITHM.md` for technical specs

## License

MIT License - See LICENSE file in repository root.
