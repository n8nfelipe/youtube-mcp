import json
import subprocess
import sys
import time

proc = subprocess.Popen(
    [sys.executable, "server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
)

try:
    proc.stdin.write(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "healthcheck", "version": "1.0"},
                },
            }
        )
        + "\n"
    )
    proc.stdin.flush()
    time.sleep(1)
    line = proc.stdout.readline()
    if not line:
        raise SystemExit("no response from server")
    resp = json.loads(line)
    if "result" not in resp:
        raise SystemExit("invalid handshake response")
    print("healthcheck ok")
except Exception as e:
    print(f"healthcheck failed: {e}", file=sys.stderr)
    raise SystemExit(1)
finally:
    proc.terminate()
