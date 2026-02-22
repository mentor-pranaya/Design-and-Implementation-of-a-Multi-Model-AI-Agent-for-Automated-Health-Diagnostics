#!/usr/bin/env python
"""Service runner for Lab Report Analyzer app.

Runs Streamlit app on port 8501 with graceful shutdown handling.
Suitable for systemd, Docker, or direct execution.
"""

import os
import sys
import subprocess
import signal

PORT = os.environ.get("PORT", "8501")
HOST = os.environ.get("HOST", "0.0.0.0")


def main():
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        f"--server.port={PORT}",
        f"--server.address={HOST}",
        "--client.showErrorDetails=true",
        "--logger.level=info",
    ]

    print(f"Starting Lab Report Analyzer on {HOST}:{PORT}...")
    print(f"Command: {' '.join(cmd)}")

    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print("Interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting app: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
