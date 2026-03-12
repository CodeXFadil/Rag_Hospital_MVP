import sys
import os

def apply_patch():
    # 1. Patch SQLite for older Linux environments (e.g. Railway/Streamlit)
    if sys.platform.startswith('linux'):
        try:
            import pysqlite3
            sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
            print("[PATCH] SQLite3 successfully patched with pysqlite3", flush=True)
        except Exception as e:
            print(f"[PATCH] SQLite3 patch skipped or failed: {e}", flush=True)

    # 2. Patch 'nn' NameError for transformers/accelerate on some environments
    # This forces torch into global namespace to satisfy leaked type hints
    try:
        import torch
        import torch.nn as nn
        # Inject into builtins so it's truly global if needed by stale type hints
        import builtins
        builtins.nn = nn
        print("[PATCH] Torch and 'nn' namespace successfully initialized", flush=True)
    except Exception as e:
        print(f"[PATCH] Torch initialization skipped: {e}", flush=True)

if __name__ == "__main__":
    apply_patch()
