import sys
import os

def apply_patch():
    if sys.platform.startswith('linux'):
        try:
            import pysqlite3
            sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
            print("[PATCH] SQLite3 successfully patched with pysqlite3", flush=True)
        except Exception as e:
            print(f"[PATCH] SQLite3 patch failed: {e}", flush=True)

if __name__ == "__main__":
    apply_patch()
