"""
EnforceSense Module Integration

This module integrates the EnforceSense debt recovery/enforcement system
as a separate module within the Infometrix platform.

Integration Method: Git Submodule
Repository: https://github.com/dje115/enforcesense
"""

from .module import EnforceSenseModule

__all__ = ['EnforceSenseModule']

