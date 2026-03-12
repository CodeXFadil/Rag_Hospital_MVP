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
    # This forces torch and common types into global namespace to satisfy leaked type hints
    try:
        import torch
        import torch.nn as nn
        import builtins
        
        # Inject core modules/classes into builtins
        builtins.torch = torch
        builtins.nn = nn
        
        # Inject common typing aliases that are sometimes leaked
        import typing
        for t in ["Optional", "Union", "List", "Dict", "Tuple", "Any"]:
            if hasattr(typing, t):
                setattr(builtins, t, getattr(typing, t))
        
        # LRScheduler is often referenced without torch.optim
        try:
            import torch.optim.lr_scheduler as lr_scheduler
            # LRScheduler might be defined differently across versions
            if hasattr(lr_scheduler, "LRScheduler"):
                builtins.LRScheduler = lr_scheduler.LRScheduler
            elif hasattr(lr_scheduler, "_LRScheduler"):
                builtins.LRScheduler = lr_scheduler._LRScheduler
        except:
            pass
        
        injected = [k for k in ["torch", "nn", "LRScheduler", "Optional"] if hasattr(builtins, k)]
        print(f"[PATCH] Global symbols ({', '.join(injected)}...) successfully initialized", flush=True)
    except Exception as e:
        print(f"[PATCH] Global symbol injection failed: {e}", flush=True)

if __name__ == "__main__":
    apply_patch()
