"""
Pytest configuration for Quiet Corner Finder.
Adds backend directory to sys.path so tests can import backend modules directly.
"""
import sys
import os

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
