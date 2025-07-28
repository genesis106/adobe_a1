import os
import json
import pdfplumber
from collections import Counter, defaultdict

def _find_header_footer_candidates(reconstructed_lines, tolerance=3):
    """Identifies potential header/footer lines based on recurrence."""
    # A line is a candidate if its text and y-position are common across pages
    line_positions = defaultdict(list)
    for line in reconstructed_lines:
        # Round y-position to group lines that are in similar vertical locations
        rounded_y = round(line['y'] / tolerance) * tolerance
        key = (line['text'], rounded_y)
        line_positions[key].append(line['page'])

    # Consider lines appearing on more than one page as candidates
    candidates = set()
    for key, pages in line_positions.items():
        if len(set(pages)) > 1:
            # Add the text content to the set of candidates
            candidates.add(key[0])
            
    return candidates

def extract_headings_by_fontsize(pdf_path, y_tolerance=2):
    """
    Extracts the title and a multi-level outline from a PDF by filtering
    headers/footers and analyzing font properties.

    Args:
        pdf_path (str): The file path to the PDF document.
        y_tolerance (int, optional): Vertical tolerance to group characters into a line.

    Returns:
        dict: A dictionary containing the 'title' and a hierarchical 'outline' list.
    """
    reconstructed_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_chars = sorted(page.chars, key=lambda c: (c['top'], c['x0']))
            if not page_chars:
                continue

            current_line_chars = [page_chars[0]]
            for char in page_chars[1:]:
                if abs(char['top'] - current_line_chars[-1]['top']) <= y_tolerance:
                    current_line_chars.append(char)
                else:
                    if current_line_chars:
                        text = ''.join([c['text'] for c in current_line_chars]).strip()
                        if text:
                            sizes = [round(c['size'], 1) for c in current_line_chars]
                            names = [c['fontname'] for c in current_line_chars]
                            reconstructed_lines.append({
                                'text': text,
                                'size': Counter(sizes).most_common(1)[0][0],
                                'fontname': Counter(names).most_common(1)[0][0],
                                'page': page_idx,
                                'y': current_line_chars[0]['top'],
                            })
                    current_line_chars = [char]
            
            if current_line_chars:
                text = ''.join([c['text'] for c in current_line_chars]).strip()
                if text:
                    sizes = [round(c['size'], 1) for c in current_line_chars]
                    names = [c['fontname'] for c in current_line_chars]
                    reconstructed_lines.append({
                        'text': text,
                        'size': Counter(sizes).most_common(1)[0][0],
                        'fontname': Counter(names).most_common(1)[0][0],
                        'page': page_idx,
                        'y': current_line_chars[0]['top'],
                    })

    if not reconstructed_lines:
        return {"title": "No Content Found", "outline": []}

    # Step 1: Filter out headers and footers
    header_footer_text = _find_header_footer_candidates(reconstructed_lines)
    main_content_lines = [
        line for line in reconstructed_lines if line['text'] not in header_footer_text
    ]

    # Step 2: Merge consecutive lines of main content into text blocks
    text_blocks = []
    if main_content_lines:
        current_block = main_content_lines[0]
        for line in main_content_lines[1:]:
            is_same_style = (line['size'] == current_block['size'] and
                             line['fontname'] == current_block['fontname'])
            is_consecutive = (line['page'] == current_block['page'] and
                              (line['y'] - current_block['y']) < (current_block['size'] * 1.5))
            ends_thought = current_block['text'].strip().endswith(('.', ':', '?', '!'))

            if is_same_style and is_consecutive and not ends_thought:
                current_block['text'] += ' ' + line['text']
                current_block['y'] = line['y'] # Update y to the last line's y
            else:
                text_blocks.append(current_block)
                current_block = line
        text_blocks.append(current_block)

    if not text_blocks:
        return {"title": "No Content Found", "outline": []}

    # Step 3: Identify potential headings based on font size
    all_font_sizes = [block['size'] for block in text_blocks]
    if not all_font_sizes:
        return {"title": "No Content Found", "outline": []}
        
    font_size_freq = Counter(all_font_sizes)
    most_common_size = font_size_freq.most_common(1)[0][0]
    
    potential_headings = [
        block for block in text_blocks
        if block['size'] > most_common_size and len(block['text']) > 2
    ]
    
    # Fallback if no headings are larger than the most common size
    if not potential_headings:
          potential_headings = [
            block for block in text_blocks
            if block['size'] >= most_common_size and len(block['text']) > 2 and not block['text'].isnumeric()
        ]

    # Step 4: Extract Title and a multi-level Outline
    title = "No Title Found"
    outline = []
    
    if potential_headings:
        # Assume the first potential heading is the title
        title_block = potential_headings[0]
        title = title_block['text']
        
        # Determine heading levels based on font size
        heading_sizes = sorted(list({h['size'] for h in potential_headings}), reverse=True)
        size_to_level_map = {size: f"H{i+1}" for i, size in enumerate(heading_sizes)}

        # Create outline, avoiding duplicates (like the title)
        used_headings = {(title.strip().lower(), title_block['page'])}
        
        for block in potential_headings:
            key = (block['text'].strip().lower(), block['page'])
            if key in used_headings:
                continue
            
            level = size_to_level_map.get(block['size'], 'H4') # Default to a lower level
            outline.append({"level": level, "text": block['text'], "page": block['page']})
            used_headings.add(key)

    return {"title": title, "outline": outline}


def main(input_dir="./input", output_dir="./output"):
    # This function remains the same, executing the logic above.
    os.makedirs(output_dir, exist_ok=True)
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    
    if not files and os.path.exists("file02.pdf"):
        files.append("file02.pdf")
        input_dir = "."
    elif not files:
        print(f"No PDF files found in '{input_dir}'")
        return
            
    for filename in files:
        pdf_path = os.path.join(input_dir, filename)
        print(f"Processing {filename} ...")
        try:
            result = extract_headings_by_fontsize(pdf_path)
            json_filename = os.path.splitext(filename)[0] + ".json"
            json_path = os.path.join(output_dir, json_filename)
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
            print(f"✔ Saved output to {json_path}\n")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        except Exception as e:
            print(f"❌ Error processing {filename}: {e}\n")


if __name__ == "__main__":
    # Setup dummy directories for execution
    os.makedirs("./input", exist_ok=True)
    os.makedirs("./output", exist_ok=True)

    # Simplified execution logic
    main()
