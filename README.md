# PDF Outline Extractor 📑

This Python script automatically extracts a structured, multi-level outline from PDF documents. It analyzes font properties (like size and name) to identify headings and distinguish them from body text, headers, and footers. The output is a clean JSON file containing the document's title and a hierarchical list of headings.

---

## ✨ Features

- **Font-Based Analysis**: Identifies headings by detecting text with a larger font size than the most common body text.
- **Header & Footer Removal**: Intelligently detects and filters out recurring text at the top and bottom of pages to avoid including them in the outline.
- **Multi-Line Heading Support**: Merges consecutive lines of text that share the same style to correctly capture multi-line headings.
- **Hierarchical Outline**: Assigns heading levels (H1, H2, H3, etc.) based on distinct font sizes, creating a structured document map.
- **JSON Output**: Saves the extracted title and outline into a well-formatted `.json` file for easy use in other applications.

---

## ⚙️ How It Works

The script follows a multi-step process to analyze a PDF and build the outline:

1. **Line Reconstruction**:  
   Iterates through every character on each page, grouping them into lines based on their vertical position (`top` coordinate). It also determines the most common font size and name for each reconstructed line.

2. **Header/Footer Filtering**:  
   Identifies potential headers and footers by detecting lines of text that appear at the same vertical position on multiple pages. These candidate lines are excluded from the main content.

3. **Text Block Merging**:  
   Merges consecutive lines with the same font style (size and name) that are close to each other. This ensures that headings spanning multiple lines are treated as a single block.

4. **Heading Identification**:  
   Assumes headings have a larger font size than body text. The most common font size is taken as body text, and any larger-size block is flagged as a potential heading.

5. **Outline Generation**:  
   The first identified heading is designated as the document title. Remaining headings are categorized into levels (H1, H2, etc.) based on their font sizes. The structure is compiled into a final JSON output.

---

## 🚀 Usage

### Requirements

- Python 3.x
- [`pdfplumber`](https://github.com/jsvine/pdfplumber)

### Installation

Install the required library using pip:

```bash
pip install pdfplumber
