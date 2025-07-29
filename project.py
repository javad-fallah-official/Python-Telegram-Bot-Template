"""
Project configuration and module registry.
Centralizes the modular structure and provides easy access to all components.
"""

from typing import Dict, Any, List
import importlib
from pathlib import Path

# Project metadata
PROJECT_NAME = "Telegram Bot Template"
PROJECT_VERSION = "2.0.0"
PROJECT_DESCRIPTION = "A highly modular Telegram bot template with advanced features"

# Module structure definition
MODULES = {
    "core": {
        "description": "Core functionality and configuration",
        "components": [
            "config",
            "logger", 
            "database",
            "middleware"
        ]
    },
    "bot": {
        "description": "Bot application and factory",
        "components": [
            "factory",
            "application",
            "handlers"
        ]
    },
    "services": {
        "description": "Service layer for different bot modes",
        "components": [
            "polling",
            "webhook"
        ]
    },
    "utils": {
        "description": "Utility functions and helpers",
        "components": [
            "formatters",
            "keyboards",
            "files",
            "text",
            "cache",
            "validators"
        ]
    }
}

# Entry points
ENTRY_POINTS = {
    "main": "main.py",
    "cli": "cli.py", 
    "run": "run.py",
    "polling": "polling.py",
    "webhook": "webhook.py",
    "example": "example_bot.py"
}

# Configuration files
CONFIG_FILES = [
    ".env",
    ".env.example",
    "pyproject.toml",
    "uv.lock"
]

# Documentation files
DOCS = [
    "README.md",
    "QUICKSTART.md"
]


class ModuleRegistry:
    """Registry for managing modular components."""
    
    def __init__(self):
        self.loaded_modules = {}
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        """Get information about a module."""
        return MODULES.get(module_name, {})
    
    def list_modules(self) -> List[str]:
        """List all available modules."""
        return list(MODULES.keys())
    
    def list_components(self, module_name: str) -> List[str]:
        """List components in a module."""
        module_info = MODULES.get(module_name, {})
        return module_info.get("components", [])
    
    def import_component(self, module_name: str, component_name: str):
        """Dynamically import a component."""
        module_path = f"{module_name}.{component_name}"
        
        if module_path not in self.loaded_modules:
            try:
                self.loaded_modules[module_path] = importlib.import_module(module_path)
            except ImportError as e:
                raise ImportError(f"Failed to import {module_path}: {e}")
        
        return self.loaded_modules[module_path]
    
    def get_project_structure(self) -> Dict[str, Any]:
        """Get the complete project structure."""
        return {
            "metadata": {
                "name": PROJECT_NAME,
                "version": PROJECT_VERSION,
                "description": PROJECT_DESCRIPTION
            },
            "modules": MODULES,
            "entry_points": ENTRY_POINTS,
            "config_files": CONFIG_FILES,
            "docs": DOCS
        }
    
    def validate_structure(self) -> List[str]:
        """Validate that all modules and components exist."""
        issues = []
        project_root = Path(__file__).parent
        
        # Check modules
        for module_name, module_info in MODULES.items():
            module_path = project_root / module_name
            if not module_path.exists():
                issues.append(f"Module directory missing: {module_name}")
                continue
            
            # Check __init__.py
            init_file = module_path / "__init__.py"
            if not init_file.exists():
                issues.append(f"Missing __init__.py in module: {module_name}")
            
            # Check components
            for component in module_info.get("components", []):
                component_file = module_path / f"{component}.py"
                if not component_file.exists():
                    issues.append(f"Missing component: {module_name}.{component}")
        
        # Check entry points
        for name, file_path in ENTRY_POINTS.items():
            entry_file = project_root / file_path
            if not entry_file.exists():
                issues.append(f"Missing entry point: {file_path}")
        
        return issues


# Global registry instance
registry = ModuleRegistry()


def get_registry() -> ModuleRegistry:
    """Get the global module registry."""
    return registry


def get_project_info() -> Dict[str, str]:
    """Get basic project information."""
    return {
        "name": PROJECT_NAME,
        "version": PROJECT_VERSION,
        "description": PROJECT_DESCRIPTION
    }


def list_available_modules() -> List[str]:
    """List all available modules."""
    return registry.list_modules()


def get_module_components(module_name: str) -> List[str]:
    """Get components for a specific module."""
    return registry.list_components(module_name)