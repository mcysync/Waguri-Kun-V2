import pkgutil
import importlib
import logging

logger = logging.getLogger("WaguriBot.Modules")

def get_all_modules() -> list[str]:
    """Returns a list of all module names in the 'modules' directory."""
    return [name for _, name, is_pkg in pkgutil.iter_modules(__path__) if not is_pkg]

# Auto-loader for initialization purposes if needed. 
# Pyrogram's dict(root="modules") handles the actual handler routing automatically.
logger.info("Initializing WaguriBot Modules Directory...")
