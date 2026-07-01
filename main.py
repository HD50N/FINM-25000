"""Entry point for the Mini Market Data Terminal."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.terminal import main

if __name__ == "__main__":
    main()
