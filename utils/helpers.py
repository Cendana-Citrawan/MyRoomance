import os
import json

def load(*file_names):
    """Load CSS/JSON files and return their contents."""
    def _load(file):
        if not os.path.exists(file):
            raise FileNotFoundError(f"[ERROR] {file} not found")
        ext = os.path.splitext(file)[1].lower()
        with open(file, encoding='utf-8') as f:
            if ext == '.css':
                return f"<style>{f.read()}</style>"
            if ext == '.json':
                return json.load(f)
            raise ValueError(f"[ERROR] Unsupported file type: {ext}")
    results = [_load(f) for f in file_names]
    return results[0] if len(results) == 1 else results