"""
Routes package exports for Quiet Corner Finder.
"""
from .spaces import spaces_bp
from .reports import reports_bp
from .stats import stats_bp
from .demo import demo_bp

__all__ = ['spaces_bp', 'reports_bp', 'stats_bp', 'demo_bp']
