import re
import fitz
from utils.logger import log_error

# Synonym groups for action verbs
_EXTRACT = r"extract|get|save|keep|grab"
_DELETE  = r"delete|remove|drop|trash|cut"
_MERGE   = r"merge|combine|join|attach|stitch"
_INSERT  = r"insert|add|place|put"
_ROTATE  = r"rotate|turn|flip"
_COMPRESS = r"compress|optimize|shrink|reduce"

# Help trigger words
_HELP_VERBS = r"how|help|what|show|explain"

def parse(command, files):
    if not command or not command.strip():
        return None

    raw = command.strip()
    cmd = re.sub(r'\band\b', ',', raw.lower())

    ref_map = {"first": 0, "second": 1, "third": 2}

    def validate_file_count(n):
        if len(files) < n:
            log_error("validation", f"Requires {n} files, got {len(files)}")
            return False
        return True

    def get_page_count(path):
        try:
            doc = fitz.open(path)
            n = len(doc)
            doc.close()
            return n
        except Exception as e:
            log_error("validation", f"Could not open PDF: {e}")
            return None

    def validate_pages(path, pages):
        n = get_page_count(path)
        if n is None:
            return False
        bad = [p for p in pages if p < 1 or p > n]
        if bad:
            log_error("validation", f"Invalid pages {bad} for {n}-page PDF")
            return False
        return True

    # ── HELP ────────────────────────────────────────────────────────────────
    # "how do I merge", "help with extract", "what is compress"
    m = re.search(rf'({_HELP_VERBS}).*?({_EXTRACT}|{_DELETE}|{_MERGE}|{_INSERT}|{_ROTATE}|{_COMPRESS}|password|rotate|grayscale|interleave|blank)', cmd)
    if m:
        return {"action": "help", "topic": m.group(2)}

    # ── INSERT RANGE ─────────────────────────────────────────────────────────
    # "insert pages 1-5 of first pdf into second pdf at page 10"
    m = re.search(
        rf'({_INSERT}) pages? (\d+)-(\d+) of (first|second|third) pdf (?:into|in) (first|second|third) pdf at page (\d+)',
        cmd)
    if m:
        if not validate_file_count(2): return None
        start, end = int(m.group(2)), int(m.group(3))
        src, tgt = files[ref_map[m.group(4)]], files[ref_map[m.group(5)]]
        if not validate_pages(src, list(range(min(start,end), max(start,end)+1))): return None
        return {"action": "insert_range", "source_file": src, "target_file": tgt,
                "start": min(start,end), "end": max(start,end), "target_page": int(m.group(6))}

    # ── INSERT SINGLE PAGE ───────────────────────────────────────────────────
    # "insert page 3 of first pdf into second pdf at page 5"
    # "add page 1 of cover.pdf to the start" → target_page=1
    m = re.search(
        rf'({_INSERT}) page (\d+) of (first|second|third) pdf (?:into|in|to) (first|second|third) pdf at page (\d+)',
        cmd)
    if m:
        if not validate_file_count(2): return None
        page = int(m.group(2))
        src, tgt = files[ref_map[m.group(3)]], files[ref_map[m.group(4)]]
        if not validate_pages(src, [page]): return None
        return {"action": "insert_cross", "source_file": src, "target_file": tgt,
                "page": page, "target_page": int(m.group(5))}

    # "add page 1 of first pdf to the start of second pdf"
    m = re.search(
        rf'({_INSERT}) page (\d+) of (first|second|third) pdf to the (start|end) of (first|second|third) pdf',
        cmd)
    if m:
        if not validate_file_count(2): return None
        page = int(m.group(2))
        src = files[ref_map[m.group(3)]]
        tgt = files[ref_map[m.group(5)]]
        if not validate_pages(src, [page]): return None
        n = get_page_count(tgt)
        target_page = 1 if m.group(4) == "start" else (n + 1 if n else 1)
        return {"action": "insert_cross", "source_file": src, "target_file": tgt,
                "page": page, "target_page": target_page}

    # ── INTERLEAVE ───────────────────────────────────────────────────────────
    # "interleave first pdf and second pdf"
    if re.search(r'interleave', cmd):
        if not validate_file_count(2): return None
        return {"action": "interleave", "source_file": files[0], "target_file": files[1]}

    # ── EXTRACT: keyword search ──────────────────────────────────────────────
    # "extract pages containing 'Invoice'"
    m = re.search(rf'({_EXTRACT}) pages? (?:containing|with|that (?:have|contain)) ["\']?(.+?)["\']?\s*$', cmd)
    if m:
        if not validate_file_count(1): return None
        return {"action": "extract_keyword", "keyword": m.group(2).strip()}

    # ── EXTRACT: first/last N pages ──────────────────────────────────────────
    # "extract the first 5 pages" / "extract last 2 pages"
    m = re.search(rf'({_EXTRACT}) (?:the )?(first|last) (\d+) pages?', cmd)
    if m:
        if not validate_file_count(1): return None
        n = int(m.group(3))
        n_pages = get_page_count(files[0])
        if n_pages is None: return None
        if m.group(2) == "first":
            start, end = 1, min(n, n_pages)
        else:
            start, end = max(1, n_pages - n + 1), n_pages
        return {"action": "extract_range", "start": start, "end": end}

    # ── EXTRACT: odd/even pages ──────────────────────────────────────────────
    m = re.search(rf'({_EXTRACT}) (?:all )?(odd|even) pages?', cmd)
    if m:
        if not validate_file_count(1): return None
        return {"action": "extract_parity", "parity": m.group(2)}

    # ── EXTRACT: reverse range "pages 10 to 1" ───────────────────────────────
    m = re.search(rf'({_EXTRACT}) pages? (\d+) to (\d+)', cmd)
    if m:
        if not validate_file_count(1): return None
        a, b = int(m.group(2)), int(m.group(3))
        pages = list(range(a, b-1, -1)) if a > b else list(range(a, b+1))
        if not validate_pages(files[0], pages): return None
        return {"action": "extract_pages", "pages": pages}

    # ── EXTRACT: numeric range ───────────────────────────────────────────────
    m = re.search(rf'({_EXTRACT}) pages? (\d+)-(\d+)', cmd)
    if m:
        if not validate_file_count(1): return None
        start, end = int(m.group(2)), int(m.group(3))
        start, end = min(start, end), max(start, end)
        if not validate_pages(files[0], list(range(start, end+1))): return None
        return {"action": "extract_range", "start": start, "end": end}

    # ── EXTRACT: list ────────────────────────────────────────────────────────
    m = re.search(rf'({_EXTRACT}) pages? ([\d ,]+)', cmd)
    if m:
        if not validate_file_count(1): return None
        pages = [int(p.strip()) for p in m.group(2).split(",") if p.strip().isdigit()]
        if pages:
            if not validate_pages(files[0], pages): return None
            return {"action": "extract_pages", "pages": pages}

    # ── DELETE: all pages after N ────────────────────────────────────────────
    # "delete all pages after 50"
    m = re.search(rf'({_DELETE}) all pages? after (\d+)', cmd)
    if m:
        if not validate_file_count(1): return None
        after = int(m.group(2))
        n_pages = get_page_count(files[0])
        if n_pages is None: return None
        if after >= n_pages: return None
        return {"action": "delete_range", "start": after + 1, "end": n_pages}

    # ── DELETE: blank pages ──────────────────────────────────────────────────
    if re.search(rf'({_DELETE}).*blank pages?', cmd):
        if not validate_file_count(1): return None
        return {"action": "delete_blank"}

    # ── DELETE: range ────────────────────────────────────────────────────────
    m = re.search(rf'({_DELETE}) pages? (\d+)-(\d+)', cmd)
    if m:
        if not validate_file_count(1): return None
        start, end = int(m.group(2)), int(m.group(3))
        start, end = min(start, end), max(start, end)
        if not validate_pages(files[0], list(range(start, end+1))): return None
        return {"action": "delete_range", "start": start, "end": end}

    # ── DELETE: list ─────────────────────────────────────────────────────────
    m = re.search(rf'({_DELETE}) pages? ([\d ,]+)', cmd)
    if m:
        if not validate_file_count(1): return None
        pages = [int(p.strip()) for p in m.group(2).split(",") if p.strip().isdigit()]
        if pages:
            if not validate_pages(files[0], pages): return None
            return {"action": "delete_pages", "pages": pages}

    # ── ROTATE ───────────────────────────────────────────────────────────────
    # "rotate page 5 clockwise", "flip all pages 180", "rotate all pages 90"
    m = re.search(rf'({_ROTATE})(?:\s+(?:page|pages?))? (\d+|all)(?: pages?)? ?(clockwise|counterclockwise|ccw|cw|180|90|270)?', cmd)
    if m:
        if not validate_file_count(1): return None
        target = m.group(2)          # page number or "all"
        direction = m.group(3) or "clockwise"
        angle_map = {"clockwise": 90, "cw": 90, "counterclockwise": 270, "ccw": 270,
                     "180": 180, "90": 90, "270": 270}
        angle = angle_map.get(direction, 90)
        if target == "all":
            pages = None  # means all pages
        else:
            pages = [int(target)]
            if not validate_pages(files[0], pages): return None
        return {"action": "rotate", "pages": pages, "angle": angle}

    # ── GRAYSCALE ────────────────────────────────────────────────────────────
    if re.search(r'grayscale|black.?and.?white|black\s*&\s*white|b&w|bw', cmd):
        if not validate_file_count(1): return None
        return {"action": "grayscale"}

    # ── COMPRESS ─────────────────────────────────────────────────────────────
    m = re.search(rf'({_COMPRESS})', cmd)
    if m:
        if not validate_file_count(1): return None
        if "high" in cmd or "printer" in cmd:
            quality = "high"
        elif "low" in cmd or "screen" in cmd or "web" in cmd:
            quality = "low"
        else:
            quality = "medium"
        return {"action": "compress", "quality": quality}

    # ── MERGE ────────────────────────────────────────────────────────────────
    m = re.search(rf'({_MERGE})', cmd)
    if m:
        if not validate_file_count(2): return None
        return {"action": "merge"}

    return None
