import subprocess
import os
from datetime import datetime
from utils.gs_utils import require_gs

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")


def compress_pdf(input_path, quality="medium"):
    """Compress PDF using Ghostscript."""
    quality_map = {"low": "screen", "medium": "ebook", "high": "printer"}
    setting = quality_map.get(quality, "ebook")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}_compressed_{timestamp}.pdf")

    gs_command = require_gs()

    command = [
        gs_command, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PDF compression failed: {e.stderr}")