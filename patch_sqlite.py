import sys
import os

def apply_patch():
    # 1. Patch SQLite for older Linux environments (e.g. Railway/Streamlit/Render)
    if sys.platform.startswith('linux'):
        try:
            import pysqlite3
            sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
            print("[PATCH] SQLite3 successfully patched with pysqlite3", flush=True)
        except Exception as e:
            print(f"[PATCH] SQLite3 patch skipped or failed: {e}", flush=True)

    # Note: Global symbol injection (nn, LRScheduler, etc.) was removed in favor 
    # of robust versioning and correct import ordering in the main entry points.

if __name__ == "__main__":
    apply_patch()
