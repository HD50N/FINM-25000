"""Run the paper trading engine headless (no UI). Ctrl-C to stop."""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.engine.live_engine import LiveTradingEngine


def main() -> None:
    engine = LiveTradingEngine()
    engine.start()
    try:
        while engine.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping…")
    finally:
        engine.stop()


if __name__ == "__main__":
    main()
