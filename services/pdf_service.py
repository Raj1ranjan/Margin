import os
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
import fitz

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_output_path(prefix="output"):
    """Generates a timestamped filename in the outputs/ directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUT_DIR, f"{prefix}_{timestamp}.pdf")

def merge_pdfs(files):
    """Merges multiple PDF files into one single document."""
    writer = PdfWriter()

    for file in files:
        try:
            reader = PdfReader(file)
            if reader.is_encrypted:
                raise ValueError(f"'{os.path.basename(file)}' is password-protected and cannot be merged.")
            for page in reader.pages:
                writer.add_page(page)
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to read '{os.path.basename(file)}': {e}")

    output_path = generate_output_path("merge")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def insert_cross_pdf(source_file, target_file, page_number, target_position):
    """Inserts a single page from a source PDF into a specific position in a target PDF."""
    source_reader = PdfReader(source_file)
    target_reader = PdfReader(target_file)
    writer = PdfWriter()

    # Get the specific page (adjusting for 0-indexing)
    insert_page = source_reader.pages[page_number - 1]

    for i, page in enumerate(target_reader.pages):
        # Insert at the target position
        if i == target_position - 1:
            writer.add_page(insert_page)
        writer.add_page(page)

    # If the target position is beyond the end of the document
    if target_position > len(target_reader.pages):
        writer.add_page(insert_page)

    output_path = generate_output_path("insert")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def insert_range_pdf(source_file, target_file, start, end, target_position):
    """Inserts a range of pages from a source PDF into a target PDF at a specific position."""
    source_reader = PdfReader(source_file)
    target_reader = PdfReader(target_file)
    writer = PdfWriter()

    # Extract the range of pages
    pages_to_insert = source_reader.pages[start - 1:end]

    for i, page in enumerate(target_reader.pages):
        if i == target_position - 1:
            for p in pages_to_insert:
                writer.add_page(p)
        writer.add_page(page)

    # If the target position is beyond the last page
    if target_position > len(target_reader.pages):
        for p in pages_to_insert:
            writer.add_page(p)

    output_path = generate_output_path("range_insert")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def extract_pages(file, pages):
    """Extracts a specific list of pages (e.g., [1, 3, 5]) into a new PDF."""
    reader = PdfReader(file)
    writer = PdfWriter()

    for p in pages:
        # Bounds checking to prevent index errors
        if 0 < p <= len(reader.pages):
            writer.add_page(reader.pages[p - 1])

    output_path = generate_output_path("extract")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def extract_range(file, start, end):
    """Extracts a continuous range of pages into a new PDF."""
    reader = PdfReader(file)
    writer = PdfWriter()

    # Ensure we don't exceed the actual page count
    total_pages = len(reader.pages)
    
    for i in range(start - 1, end):
        if 0 <= i < total_pages:
            writer.add_page(reader.pages[i])

    output_path = generate_output_path("extract_range")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def delete_pages(file, pages_to_delete):
    """Deletes specific pages from a PDF based on a list of page numbers."""
    reader = PdfReader(file)
    writer = PdfWriter()

    # Using a set for O(1) lookups during the loop
    pages_to_delete_set = set(pages_to_delete)

    for i, page in enumerate(reader.pages, start=1):
        if i not in pages_to_delete_set:
            writer.add_page(page)

    output_path = generate_output_path("delete_pages")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def delete_range(file, start, end):
    """Deletes a continuous range of pages from a PDF."""
    reader = PdfReader(file)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages, start=1):
        # Only add pages that fall outside the specified range
        if not (start <= i <= end):
            writer.add_page(page)

    output_path = generate_output_path("delete_range")
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path

def extract_parity(file, parity):
    """Extracts all odd or even pages from a PDF."""
    reader = PdfReader(file)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        if (parity == "even" and i % 2 == 0) or (parity == "odd" and i % 2 != 0):
            writer.add_page(page)
    output_path = generate_output_path(f"extract_{parity}")
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def extract_keyword(file, keyword):
    """Extracts pages that contain the given keyword (case-insensitive)."""
    doc = fitz.open(file)
    writer = PdfWriter()
    reader = PdfReader(file)
    matched = []
    for i, page in enumerate(doc):
        if keyword.lower() in page.get_text().lower():
            matched.append(i)
    doc.close()
    if not matched:
        raise ValueError(f"No pages found containing '{keyword}'")
    for i in matched:
        writer.add_page(reader.pages[i])
    output_path = generate_output_path("extract_keyword")
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def delete_blank(file):
    """Removes pages that contain no meaningful content (blank pages)."""
    doc = fitz.open(file)
    reader = PdfReader(file)
    writer = PdfWriter()
    for i, page in enumerate(doc):
        # A page is blank if it has no text and no images
        if page.get_text().strip() or page.get_images():
            writer.add_page(reader.pages[i])
    doc.close()
    output_path = generate_output_path("delete_blank")
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def interleave_pdfs(file_a, file_b):
    """Interleaves pages from two PDFs (A1, B1, A2, B2, ...)."""
    reader_a = PdfReader(file_a)
    reader_b = PdfReader(file_b)
    writer = PdfWriter()
    len_a, len_b = len(reader_a.pages), len(reader_b.pages)
    for i in range(max(len_a, len_b)):
        if i < len_a:
            writer.add_page(reader_a.pages[i])
        if i < len_b:
            writer.add_page(reader_b.pages[i])
    output_path = generate_output_path("interleave")
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def rotate_pages(file, pages, angle):
    """Rotates specified pages (or all if pages=None) by the given angle."""
    reader = PdfReader(file)
    writer = PdfWriter()
    rotate_set = set(pages) if pages else None
    for i, page in enumerate(reader.pages, start=1):
        if rotate_set is None or i in rotate_set:
            page.rotate(angle)
        writer.add_page(page)
    output_path = generate_output_path("rotate")
    with open(output_path, "wb") as f:
        writer.write(f)
    return output_path

def convert_grayscale(file):
    """Converts all pages to grayscale using Ghostscript, preserving text and vectors."""
    import subprocess
    from utils.gs_utils import require_gs
    gs = require_gs()
    output_path = generate_output_path("grayscale")
    subprocess.run([
        gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        "-sColorConversionStrategy=Gray", "-dProcessColorModel=/DeviceGray",
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", file
    ], check=True, capture_output=True, text=True)
    return output_path
