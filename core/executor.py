from services.pdf_service import (
    merge_pdfs, insert_cross_pdf, insert_range_pdf,
    extract_pages, extract_range, extract_parity, extract_keyword,
    delete_pages, delete_range, delete_blank,
    interleave_pdfs, rotate_pages, convert_grayscale
)
from services.pdf_compressor import compress_pdf

# Help text per topic
HELP_TEXT = {
    "extract": "Try: 'extract pages 1-5', 'extract last 3 pages', 'extract odd pages', 'extract pages containing \"Invoice\"'",
    "get":     "Try: 'get pages 1-5' or 'grab pages 2, 4, 6'",
    "delete":  "Try: 'delete pages 3-7', 'remove blank pages', 'delete all pages after 50'",
    "remove":  "Try: 'remove pages 1, 3, 5' or 'remove blank pages'",
    "merge":   "Try: 'merge', 'combine all', 'join' — select 2+ files first",
    "combine": "Try: 'combine all' — select 2+ files first",
    "insert":  "Try: 'insert page 1 of first pdf into second pdf at page 5'",
    "rotate":  "Try: 'rotate page 3 clockwise', 'rotate all pages 180'",
    "compress": "Try: 'compress high', 'compress low', 'optimize for web'",
    "shrink":  "Try: 'shrink file size' or 'compress medium'",
    "grayscale": "Try: 'convert to grayscale' or 'black and white'",
    "interleave": "Try: 'interleave first pdf and second pdf' — select 2 files first",
    "blank":   "Try: 'remove blank pages'",
    "password": "Password protection is not yet supported.",
}

def execute(intent, state):
    action = intent["action"]

    if action == "help":
        topic = intent.get("topic", "")
        return ("help", HELP_TEXT.get(topic, "Try commands like: 'extract pages 1-5', 'merge', 'compress high', 'rotate all pages 90'"))

    if action == "merge":
        return merge_pdfs(state.selected_files)

    if action == "insert_cross":
        return insert_cross_pdf(intent["source_file"], intent["target_file"],
                                intent["page"], intent["target_page"])

    if action == "insert_range":
        return insert_range_pdf(intent["source_file"], intent["target_file"],
                                intent["start"], intent["end"], intent["target_page"])

    if action == "extract_pages":
        return extract_pages(state.selected_files[0], intent["pages"])

    if action == "extract_range":
        return extract_range(state.selected_files[0], intent["start"], intent["end"])

    if action == "extract_parity":
        return extract_parity(state.selected_files[0], intent["parity"])

    if action == "extract_keyword":
        return extract_keyword(state.selected_files[0], intent["keyword"])

    if action == "delete_pages":
        return delete_pages(state.selected_files[0], intent["pages"])

    if action == "delete_range":
        return delete_range(state.selected_files[0], intent["start"], intent["end"])

    if action == "delete_blank":
        return delete_blank(state.selected_files[0])

    if action == "interleave":
        return interleave_pdfs(intent["source_file"], intent["target_file"])

    if action == "rotate":
        return rotate_pages(state.selected_files[0], intent["pages"], intent["angle"])

    if action == "grayscale":
        return convert_grayscale(state.selected_files[0])

    if action == "compress":
        return compress_pdf(state.selected_files[0], intent.get("quality", "medium"))

    return "Unknown command"
