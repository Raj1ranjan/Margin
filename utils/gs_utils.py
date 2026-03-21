import subprocess
import platform


def get_gs_command():
    """Return the platform-appropriate Ghostscript command name."""
    if platform.system() == "Windows":
        return "gswin64c.exe" if _gs_exists("gswin64c.exe") else "gswin32c.exe"
    return "gs"


def _gs_exists(cmd):
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def require_gs():
    """Return the GS command or raise RuntimeError if not found."""
    cmd = get_gs_command()
    if not _gs_exists(cmd):
        raise RuntimeError(
            "Ghostscript not found. Please install it:\n"
            "• Linux: sudo apt-get install ghostscript\n"
            "• macOS: brew install ghostscript\n"
            "• Windows: https://www.ghostscript.com/"
        )
    return cmd
