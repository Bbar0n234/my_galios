from .GFpn_field import GFpn

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

__all__ = (
    "GFpn",
)