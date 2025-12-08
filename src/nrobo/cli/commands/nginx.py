import argparse
import os
import sys
from pathlib import Path

import psutil

from nrobo.core import settings
from nrobo.services.nginx_service import reuse_or_launch_allure_nginx
from nrobo.services.nginx_service_state import clear_state, load_state


def _pid_running(pid: int) -> bool:
    try:
        p = psutil.Process(pid)
        return p.is_running() and "nginx" in p.name().lower()
    except Exception:
        return False


def cmd_start(args):
    try:
        allure_dir = Path(args.dir).resolve()
    except Exception:
        print("Incorrect command usage error!")
        run(argv=["start", "-h"])
        sys.exit(1)
        return
    result = reuse_or_launch_allure_nginx(str(allure_dir))
    print(f"🚀 Allure report served at: {result['url']}")


def cmd_status(args):
    state = load_state()
    if not state:
        print("⚠️  No Nginx state found. No server appears to be running.")
        return

    pid_file = Path(state["runtime_dir"]) / "logs" / "nginx.pid"
    pid = int(pid_file.read_text()) if pid_file.is_file() else None
    running = _pid_running(pid) if pid else False

    print("── nRoBo Nginx Status ──")
    print(f"URL:         {state['url']}")
    print(f"PID:         {pid or '—'}")
    print(f"Alive:       {'Yes ✅' if running else 'No ❌'}")
    print(f"Port:        {state['port']}")
    print(f"Directory:   {state['served_dir']}")
    print(f"Runtime dir: {state['runtime_dir']}")

    if not running:
        print("💤 Nginx PID exists but not active or listening.")


def cmd_stop(args):
    state = load_state()
    if not state:
        print("⚠️  No Nginx state file found — nothing to stop.")
        return

    pid_file = Path(state["runtime_dir"]) / "logs" / "nginx.pid"
    if not pid_file.is_file():
        print("⚠️  PID file missing — cleaning stale state.")
        clear_state()
        return

    pid = int(pid_file.read_text().strip())
    try:
        os.kill(pid, 15)
        clear_state()
        print(f"🛑 Stopped nginx (PID {pid}) and cleared state.")
    except ProcessLookupError:
        print("⚠️  Process not found — removing stale state.")
        clear_state()
    except Exception as e:
        print(f"❌ Failed to stop nginx: {e}")


def run(argv=None):
    parser = argparse.ArgumentParser(
        description=f"Manage {settings.NROBO_APP}'s local Nginx server for Allure reports."
    )
    sub = parser.add_subparsers(dest="command")

    p_start = sub.add_parser("start", help="Start (or reuse) the Nginx server")
    p_start.add_argument("--dir", help="Path to the Allure report directory")
    p_start.set_defaults(func=cmd_start)

    p_status = sub.add_parser("status", help="Show Nginx server status")
    p_status.set_defaults(func=cmd_status)

    p_stop = sub.add_parser("stop", help="Stop the running Nginx server")
    p_stop.set_defaults(func=cmd_stop)

    args = parser.parse_args(argv)

    # ✅ Safety guard: show help if no command provided
    if not hasattr(args, "func"):
        parser.print_help()
        raise SystemExit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"nginx server could not be started due to error: {e}")
