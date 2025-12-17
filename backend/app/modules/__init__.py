"""
Infometrix Platform Modules

This package contains all platform modules.
Modules are self-contained units that can be enabled/disabled per tenant.
"""

from .registry import ModuleRegistry, get_module_registry

# Import modules to register them
from .helpdesk import HelpdeskModule
from .enforcesense import EnforceSenseModule

# Initialize registry and register modules
_registry = get_module_registry()

# Register all modules
helpdesk_module = HelpdeskModule()
enforcesense_module = EnforceSenseModule()

_registry.register(helpdesk_module)
_registry.register(enforcesense_module)

__all__ = ['ModuleRegistry', 'get_module_registry', 'helpdesk_module', 'enforcesense_module']
