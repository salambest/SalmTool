"""
Log Analyzer module.

Reads Android logcat (requires root — unprivileged apps can only see
their own log lines from Android 4.1 onward) and/or Termux log files, then
flags lines that look like errors, warnings, or crashes.
"""

import os
import glob

from modules.root_manager import is_rooted, run_as_root

ERROR_KEYWORDS = ["FATAL EXCEPTION", "ERROR", "Exception", "crash", "ANR", "SIGSEGV", "Caused by"]
WARNING_KEYWORDS = ["WARNING", "WARN", "deprecated"]

TERMUX_LOG_GLOBS = [
    os.path.expanduser("~/../usr/var/log/*.log"),
    "/data/data/com.termux/files/usr/var/log/*.log",
]


def read_logcat(max_lines=500):
    if not is_rooted():
        return None
    output = run_as_root(f"logcat -d -t {max_lines}")
    if output is None:
        return None
    return output.splitlines()


def read_termux_logs():
    lines = []
    for pattern in TERMUX_LOG_GLOBS:
        for path in glob.glob(pattern):
            try:
                with open(path, "r", errors="ignore") as f:
                    lines.extend(f.readlines())
            except Exception:
                continue
    return lines


def classify_lines(lines):
    errors, warnings, crashes = [], [], []
    for line in lines:
        lower = line.lower()
        if "fatal exception" in lower or "crash" in lower or "anr" in lower:
            crashes.append(line.strip())
        elif any(k.lower() in lower for k in ERROR_KEYWORDS):
            errors.append(line.strip())
        elif any(k.lower() in lower for k in WARNING_KEYWORDS):
            warnings.append(line.strip())
    return {"errors": errors[-100:], "warnings": warnings[-100:], "crashes": crashes[-50:]}


def analyze_logs():
    logcat_lines = read_logcat() or []
    termux_lines = read_termux_logs()
    all_lines = logcat_lines + termux_lines

    classified = classify_lines(all_lines)
    classified["source_available"] = {
        "logcat": logcat_lines != [],
        "termux": termux_lines != [],
    }
    classified["total_lines_scanned"] = len(all_lines)
    return classified
