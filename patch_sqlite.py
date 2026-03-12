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

    # 2. Patch missing symbols for transformers/accelerate on some environments
    # This forces torch into global namespace to satisfy leaked type hints
    try:
        import torch
        import torch.nn as nn
        
        # Commonly leaked symbols in transformers/accelerate type hints
        import builtins
        builtins.nn = nn
        
        # LRScheduler is often referenced without torch.optim
        try:
            import torch.optim.lr_scheduler as lr_scheduler
            builtins.LRScheduler = lr_scheduler.LRScheduler
        except AttributeError:
            # Fallback for older torch versions where it was just _LRScheduler
            try:
                builtins.LRScheduler = torch.optim.lr_scheduler._LRScheduler
            except:
                pass
        
        print(f"[PATCH] Torch and symbols ({', '.join([k for k in ['nn', 'LRScheduler'] if hasattr(builtins, k)])}) successfully initialized", flush=True)
    except Exception as e:
        print(f"[PATCH] Global symbol injection skipped/failed: {e}", flush=True)

if __name__ == "__main__":
    apply_patch()
