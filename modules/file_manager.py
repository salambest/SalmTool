"""
File Manager module.

Lightweight on-device file browser helpers: recursive search by name
pattern, per-file metadata, hashing, and a bulk report generator for a set
of files.
"""

import os
import fnmatch
import time

from modules.hash_checker import compute_sha256


def search_files(root_dir, pattern="*", max_results=200):
    matches = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(dirpath, filename))
            if len(matches) >= max_results:
                return matches
    return matches


def _human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def get_file_info(path):
    try:
        stat = os.stat(path)
        return {
            "path": path,
            "size_bytes": stat.st_size,
            "size_human": _human_size(stat.st_size),
            "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
            "is_dir": os.path.isdir(path),
        }
    except Exception as e:
        return {"path": path, "error": str(e)}


def generate_file_hash(path):
    try:
        return compute_sha256(path)
    except Exception:
        return None


def build_files_report(paths):
    report = []
    for p in paths:
        info = get_file_info(p)
        if not info.get("is_dir") and "error" not in info:
            info["sha256"] = generate_file_hash(p)
        report.append(info)
    return report
