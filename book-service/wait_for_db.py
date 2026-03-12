#!/usr/bin/env python3
"""Wait for database host:port to be reachable. Uses env DB_HOST and DB_PORT (default 3306)."""
import os
import socket
import sys
import time

host = os.environ.get("DB_HOST", "")
port = int(os.environ.get("DB_PORT", "3306"))
if not host:
    print("DB_HOST not set, skipping wait")
    sys.exit(0)
for i in range(60):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((host, port))
        s.close()
        print(f"DB at {host}:{port} is ready")
        sys.exit(0)
    except Exception:
        time.sleep(1)
print("Timeout waiting for DB", file=sys.stderr)
sys.exit(1)
