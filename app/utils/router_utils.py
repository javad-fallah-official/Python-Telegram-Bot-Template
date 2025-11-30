from aiogram import Router
from aiogram.filters import Command

def get_router_commands(router: Router) -> str:
    """
    Extracts commands and their descriptions from a router.
    Returns a formatted string list.
    """
    commands = []
    seen = set()
    
    # Access the message observer directly
    observer = router.message
    
    for handler in observer.handlers:
        # Check filters for Command
        cmds = []
        for filter_obj in handler.filters:
            if hasattr(filter_obj, "callback"):
                filter_instance = filter_obj.callback
                if isinstance(filter_instance, Command):
                    # filter_instance.commands is a tuple of command strings
                    cmds.extend(filter_instance.commands)
        
        if not cmds:
            continue
            
        # Get description from docstring
        func = handler.callback
        doc = (func.__doc__ or "").strip().split("\n")[0]
        if not doc:
            doc = "No description"
            
        for cmd in cmds:
            if isinstance(cmd, str) and cmd not in seen:
                commands.append(f"/{cmd} - {doc}")
                seen.add(cmd)
                
    return "\n".join(sorted(commands))
