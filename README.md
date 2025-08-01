# Code Reader

**Code Reader** is a collection of GUI-based tools built with Python and Tkinter for reading, viewing, and analyzing source code from various programming languages. It supports automatic encoding detection, file filtering, and folder scanning, making it ideal for developers reviewing projects in C#, Python, MQL5, and more.

## Features

- **Multi-Language Support**: View code from C# (including Blazor projects), Python (.py, .ipynb, .pyw), MQL5 (.mq5, .mqh), Markdown (.md), and web files (.html, .css, .js).
- **Smart Filtering**: 
  - Exclude auto-generated files, templates, and specific directories (e.g., `__pycache__`, `bin`, `obj`).
  - Advanced filtering for Blazor projects to focus on user-modified code (e.g., GTD-related files, excluding Identity templates).
- **Encoding Detection**: Uses `chardet` to automatically detect and handle file encodings.
- **GUI Interface**: Tkinter-based UI with file/folder selection, refresh buttons, checkboxes for file types, and scrollable text views.
- **Manual Selection Mode**: Treeview-based file selector for manual picking of files to view.
- **Statistics and Logs**: Displays file counts, exclusions, and analysis summaries.

Key tools included:
- `C#SharpBlazorReader.pyw`: Filtered viewer for C# Blazor projects.
- `CSharpCodeReader.py`: General C# project viewer.
- `PythonCodeReader.pyw`: Python project scanner with folder exclusions.
- `MQL5CodeReader.pyw`: MQL5 file viewer.
- `MDReader.pyw`: Markdown file viewer.
- And more specialized readers.

## Installation

### Prerequisites
- Python 3.9 or higher.
- Tkinter (usually included with Python; install via `apt install python3-tk` on Linux if needed).
- Dependencies: `chardet` (for encoding detection).

### Using uv (Recommended)
If you have [uv](https://github.com/astral-sh/uv) installed:
```bash
uv sync
```

### Using pip
```bash
pip install -r requirements.txt
```
Or directly from `pyproject.toml`:
```bash
pip install .
```

## Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/code-reader.git
   cd code-reader
   ```

2. Run a specific tool:
   ```bash
   python CSharpBlazorReader.pyw  # For Blazor projects
   python PythonCodeReader.pyw    # For Python projects
   # Or double-click .pyw files on Windows for GUI launch
   ```

3. In the GUI:
   - Click "Open .sln file" or "Select Folder" to load projects.
   - Use checkboxes to filter file types (e.g., .cs, .razor, .json).
   - Refresh to reload changes.
   - View filtered code, statistics, and content in the text area.


## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

If you find this project useful, give it a ⭐ on GitHub! For issues or suggestions, open an [issue](https://github.com/yourusername/code-reader/issues).
