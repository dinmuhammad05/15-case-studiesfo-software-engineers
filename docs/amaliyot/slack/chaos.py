"""Gateway'ni o'ldiradi va qaytaradi. TAYYOR — o'zgartirish shart emas."""
import os
import signal
import subprocess
import time


def pids_on_port(port: int) -> list[int]:
    try:
        out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True)
    except subprocess.CalledProcessError:
        return []
    return [int(p) for p in out.split()]


def kill_gateway(port: int) -> bool:
    pids = pids_on_port(port)
    for pid in pids:
        os.kill(pid, signal.SIGKILL)   # SIGTERM emas: draining'siz qattiq o'lim
    return bool(pids)


def start_gateway(port: int) -> subprocess.Popen:
    env = {**os.environ, "PORT": str(port)}
    return subprocess.Popen(["python", "gateway.py"], env=env)


def outage(port: int, seconds: float = 10.0):
    """Gateway'ni o'ldiradi, kutadi, qaytaradi. Voqealar jurnalini qaytaradi."""
    events = []
    t0 = time.monotonic()
    ok = kill_gateway(port)
    events.append(("kill", port, time.monotonic() - t0, ok))
    time.sleep(seconds)
    start_gateway(port)
    events.append(("start", port, time.monotonic() - t0, True))
    time.sleep(2)  # ko'tarilishini kutamiz
    return events


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    for e in outage(port):
        print(e)
