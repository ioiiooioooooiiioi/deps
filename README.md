## Description
A Python tool for generating Mermaid.js dependency diagrams from a TypeScript/JavaScript project. It scans your codebase, identifies import dependencies, and provides a clear visualization of project structure.

## Requirements
- Python 3.12+
- Mermaid compatible viewer/editor (https://mermaid.live/, for example)

## Usage

```bash
python main.py /path/to/your/project > diagram.md
```

Then open `diagram.md` in a Mermaid viewer/editor to visualize your dependency graph.

## Example Output
```mermaid
graph LR
    src_utils_helpers_js["src/utils/helpers.js"] --> src_components_Button_js["src/components/Button.js"]
    src_components_Button_js["src/components/Button.js"] --> src_styles_button_css["src/styles/button.css"]
```

## License
MIT
