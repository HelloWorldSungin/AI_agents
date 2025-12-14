#!/usr/bin/env python3
"""
Allow running the autonomous module directly.

Usage:
    python -m scripts.autonomous start
    python -m scripts.autonomous status
    python -m scripts.autonomous stop
"""

from .cli import main

if __name__ == "__main__":
    main()
