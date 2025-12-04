import hashlib
import http
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import psutil

from nrobo.helpers.logging_helper import get_logger
from nrobo.helpers.network_utils import (
    find_free_port,
    is_port_in_use,
    wait_until_listening,
)
from nrobo.services.nginx_service_state import (
    clear_state,
    load_state,
    save_state,
    user_cache_dir,
)

logger = get_logger(name="nrobo.nginx")


def _stable_prefix_for_dir(serve_root: Path) -> Path:
    """Return a stable per-user prefix dir for this report folder."""
    h = hashlib.sha1(serve_root.resolve().as_posix().encode("utf-8")).hexdigest()[:10]  # nosec B324
    base = Path(user_cache_dir("nrobo")) / "nginx"
    prefix = base / f"allure-{h}"
    prefix.mkdir(parents=True, exist_ok=True)
    (prefix / "conf").mkdir(exist_ok=True)
    (prefix / "logs").mkdir(exist_ok=True)
    return prefix


def reuse_or_launch_allure_nginx(allure_report_dir: str, open_browser: bool = False) -> dict:
    root = Path(allure_report_dir).resolve()
    if root.is_file():
        root = root.parent
    if not (root / "index.html").is_file():
        raise FileNotFoundError(f"Expected index.html in: {root}")

    prefix = _stable_prefix_for_dir(root)
    pid_file = prefix / "logs" / "nginx.pid"

    state = load_state() or {}
    prev_dir = Path(state.get("served_dir", "")).resolve() if state.get("served_dir") else None
    prev_port = state.get("port")
    prev_prefix = Path(state.get("runtime_dir", "")) if state.get("runtime_dir") else None

    # Reuse ONLY if same directory + same prefix + process alive + port listening
    if (
        prev_dir
        and prev_dir == root
        and prev_prefix
        and prev_prefix == prefix
        and pid_file.is_file()
    ):
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)  # process exists
            if prev_port and is_port_in_use(prev_port, host="127.0.0.1"):
                # extra sanity: quick HTTP HEAD ok to skip; optional
                url = f"http://127.0.0.1:{prev_port}/"
                return {
                    "url": url,
                    "port": prev_port,
                    "runtime_dir": str(prefix),
                    "served_dir": str(root),
                    "mode": "user-local",
                }
        except Exception:  # nosec B110
            pass  # fall through to (re)start

    # (Re)start user-local nginx with a stable prefix and stable-or-new port
    # Try previous port first; if occupied by someone else, pick a new free one
    port_to_use = (
        prev_port
        if (
            prev_dir == root
            and prev_prefix == prefix
            and prev_port
            and not is_port_in_use(prev_port, "127.0.0.1")
        )
        else None
    )
    if port_to_use is None:
        port_to_use = find_free_port()

    conf_path = _write_user_local_conf(prefix, root, port_to_use)
    # validate
    subprocess.run(
        [_which("nginx") or "/usr/local/bin/nginx", "-t", "-p", str(prefix), "-c", str(conf_path)],
        check=True,
    )

    # reload if pid exists; else start fresh
    nginx_bin = _which("nginx") or "/usr/local/bin/nginx"
    if pid_file.exists():
        try:
            subprocess.run(
                [nginx_bin, "-p", str(prefix), "-c", str(conf_path), "-s", "reload"], check=True
            )
        except Exception:
            subprocess.run([nginx_bin, "-p", str(prefix), "-c", str(conf_path)], check=True)
    else:
        subprocess.run([nginx_bin, "-p", str(prefix), "-c", str(conf_path)], check=True)

    if not wait_until_listening(port=port_to_use, host="127.0.0.1", timeout=6):
        raise RuntimeError(f"Nginx didn’t start on 127.0.0.1:{port_to_use}")

    url = f"http://127.0.0.1:{port_to_use}/"
    if open_browser:
        try:
            import webbrowser

            webbrowser.open(url)
        except Exception:  # nosec B110
            pass

    # persist
    new_state = {
        "url": url,
        "port": port_to_use,
        "served_dir": str(root),
        "runtime_dir": str(prefix),
        "mode": "user-local",
    }
    save_state(new_state)
    return new_state


def _pid_running(pid_file: Path, expected_prefix: Path) -> bool:
    try:
        pid = int(pid_file.read_text().strip())
    except Exception:
        return False
    try:
        p = psutil.Process(pid)
        if "nginx" not in p.name().lower():
            return False
        # Confirm it's our instance (has -p <prefix>)
        cmdline = " ".join(p.cmdline())
        if str(expected_prefix) not in cmdline:
            return False
        # Check it actually listens on TCP sockets
        for conn in p.connections(kind="inet"):
            if conn.status == psutil.CONN_LISTEN:
                return True
        # Fallback: double-check via lsof
        res = subprocess.run(
            ["lsof", "-iTCP", "-a", f"-p{pid}", "-sTCP:LISTEN"],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and "nginx" in res.stdout:
            return True
        return False
    except Exception:
        return False


def _http_header_matches(host: str, port: int, expected_dir: str) -> bool:
    try:
        conn = http.client.HTTPConnection(host, port, timeout=1.5)
        conn.request("HEAD", "/")
        resp = conn.getresponse()
        # 200/301/302 are fine for Allure; check header when present
        served_from = resp.getheader("X-nRoBo-Served-From")
        conn.close()
        return (served_from is None) or (
            Path(served_from).resolve().as_posix() == Path(expected_dir).resolve().as_posix()
        )
    except Exception:
        return False


def _user_local_alive(runtime_dir: str, host: str, port: int, expected_dir: str) -> bool:
    """
    Return True only if the user-local nginx instance is genuinely alive
    and serving the expected directory. Cleans up stale masters if needed.
    """
    prefix = Path(runtime_dir)
    pid_file = prefix / "logs" / "nginx.pid"

    # PID file must exist
    if not pid_file.is_file():
        return False

    # Read PID
    try:
        pid = int(pid_file.read_text().strip())
    except Exception:
        return False

    # Check if process is alive and is nginx
    try:
        p = psutil.Process(pid)
        if "nginx" not in p.name().lower():
            return False
    except psutil.NoSuchProcess:
        return False
    except Exception:
        return False

    # Verify the process command line actually points to our prefix
    try:
        cmdline = " ".join(p.cmdline())
        if str(prefix) not in cmdline:
            # Not our instance — ignore it
            return False
    except Exception:  # nosec B110
        pass  # skip if psutil can't read cmdline

    # Now verify that it is actually listening on the port
    listening = False
    try:
        for conn in p.connections(kind="inet"):
            if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                listening = True
                break
    except Exception:  # nosec B110
        pass

    # Fallback: use lsof to cross-check (macOS-friendly)
    if not listening:
        try:
            res = subprocess.run(
                ["lsof", "-iTCP:%d" % port, "-sTCP:LISTEN"],
                capture_output=True,
                text=True,
            )
            if res.returncode == 0 and "nginx" in res.stdout:
                listening = True
        except Exception:  # nosec B110
            pass

    # If it's alive but not listening, clean up the zombie
    if not listening:
        try:
            os.kill(pid, 15)
            pid_file.unlink(missing_ok=True)
            logger.warning(
                f"🧹 Cleaned up stale nginx master (PID {pid}) — not listening on port {port}"
            )
        except Exception:  # nosec B110
            pass
        return False

    # Last sanity check: make sure the served dir matches
    if not _http_header_matches(host, port, expected_dir):
        return False

    logger.info(
        f"♻️ Reusing user-local nginx (PID {pid}) at http://{host}:{port}/ for {expected_dir}"
    )
    return True


@dataclass(frozen=True)
class NginxServeResult:
    url: str
    port: int
    root_dir: str
    nginx_path: str
    mode: str  # "user-local" | "system"
    runtime_dir: str  # user-local runtime prefix (logs, conf, etc.)


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def _detect_os() -> str:
    plat = sys.platform
    if plat.startswith("linux"):
        return "linux"
    if plat == "darwin":
        return "mac"
    if plat.startswith("win"):
        return "windows"
    return "unknown"


def _install_nginx_if_missing() -> str | None:
    """
    Try to ensure nginx is present. Return absolute path to nginx if available.
    We keep it non-fatal; caller can surface a helpful message if still missing.
    """
    path = _which("nginx")
    if path:
        return path

    os_name = _detect_os()
    try_cmds: list[list[str]] = []

    if os_name == "mac":
        # Homebrew
        if _which("brew"):
            try_cmds.append(["brew", "install", "nginx"])
    elif os_name == "linux":
        # Try apt, then yum/dnf, then pacman (best effort)
        if _which("apt"):
            try_cmds.append(["sudo", "apt", "update"])
            try_cmds.append(["sudo", "apt", "install", "-y", "nginx"])
        elif _which("apt-get"):
            try_cmds.append(["sudo", "apt-get", "update"])
            try_cmds.append(["sudo", "apt-get", "install", "-y", "nginx"])
        elif _which("dnf"):
            try_cmds.append(["sudo", "dnf", "install", "-y", "nginx"])
        elif _which("yum"):
            try_cmds.append(["sudo", "yum", "install", "-y", "nginx"])
        elif _which("pacman"):
            try_cmds.append(["sudo", "pacman", "-Sy", "nginx"])
    elif os_name == "windows":
        # Winget (Windows 10/11). This needs a user-confirmation UI in some cases.
        if _which("winget"):
            try_cmds.append(
                ["winget", "install", "--id", "Nginx.Nginx", "-e", "--source", "winget"]
            )

    # Try to run install commands (best effort)
    for cmd in try_cmds:
        try:
            logger.info(f"Attempting to install nginx via: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        except Exception as e:
            logger.warning(f"Install attempt failed: {e}")

    return _which("nginx")


def _write_user_local_conf(prefix: Path, serve_root: Path, port: int) -> Path:
    conf_dir = prefix / "conf"
    logs_dir = prefix / "logs"
    conf_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    root_abs = serve_root.resolve()
    index_html = root_abs / "index.html"
    if not index_html.is_file():
        raise FileNotFoundError(f"Allure report directory missing index.html: {root_abs}")

    nginx_conf = f"""
worker_processes 1;

error_log  {logs_dir.as_posix()}/error.log info;
pid        {logs_dir.as_posix()}/nginx.pid;

events {{
    worker_connections 1024;
}}

http {{
    types {{
        text/html  html htm shtml;
        text/css   css;
        application/javascript js;
        application/json json;
        image/png  png;
        image/jpeg jpg jpeg;
        image/svg+xml svg svgz;
        font/woff2 woff2;
        font/woff  woff;
        font/ttf   ttf;
        video/mp4  mp4;
        video/webm webm;
        application/pdf pdf;
    }}
    default_type application/octet-stream;

    access_log {logs_dir.as_posix()}/access.log;

    sendfile on;
    keepalive_timeout 65;

    server {{
        listen 127.0.0.1:{port};
        server_name localhost;

        # Serve *exactly* this directory at /
        location / {{
            alias {root_abs.as_posix()}/;
            index index.html;
            try_files $uri $uri/ /index.html;
            add_header X-nRoBo-Served-From "{root_abs.as_posix()}" always;
            # temporarily helpful while debugging:
            # autoindex on;
        }}
    }}
}}
""".strip()

    conf_path = conf_dir / "nginx.conf"
    conf_path.write_text(nginx_conf, encoding="utf-8")
    return conf_path


def _start_user_local_nginx(nginx_path: str, prefix: Path, conf_path: Path) -> None:
    """
    Start a user-local Nginx instance with -p (prefix) and -c (conf).
    Idempotent: if already running, we reload instead.
    """
    pid_file = prefix / "logs" / "nginx.pid"
    if pid_file.exists():
        # Try reload if running
        try:
            subprocess.run(
                [nginx_path, "-p", str(prefix), "-c", str(conf_path), "-s", "reload"],
                check=True,
                capture_output=True,
                text=True,
            )
            logger.info("🔁 Reloaded existing user-local Nginx.")
            return
        except Exception as e:
            logger.warning(f"Reload failed, trying fresh start: {e}")

    # Fresh start
    subprocess.run(
        [nginx_path, "-p", str(prefix), "-c", str(conf_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    logger.info("🚀 Started user-local Nginx instance.")


def _reload_system_nginx() -> None:
    """
    Attempt to reload a system-wide nginx (requires privileges).
    Tries common service managers; best effort.
    """
    candidates = [
        ["sudo", "nginx", "-s", "reload"],
        ["sudo", "systemctl", "reload", "nginx"],
        ["sudo", "service", "nginx", "reload"],
        ["nginx", "-s", "reload"],  # in case user runs shell as admin
    ]
    for cmd in candidates:
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"🔁 System nginx reloaded via: {' '.join(cmd)}")
            return
        except Exception:  # nosec B112
            continue
    raise RuntimeError(
        "Failed to reload system-wide nginx. Try running with sudo/admin privileges."
    )


def serve_allure_via_nginx(
    allure_report_dir: str | os.PathLike,
    port: int | None = None,
    prefer_system: bool = False,
    open_browser: bool = False,
) -> NginxServeResult:
    """
    Single-call helper:
      - ensures nginx exists (tries to install if missing),
      - allocates a free port (if not provided),
      - configures nginx to serve allure_report_dir,
      - starts or reloads nginx,
      - returns the URL.

    By default runs a USER-LOCAL Nginx instance (no sudo, no system files).
    Set prefer_system=True to attempt a system-wide reload (requires privileges).
    """
    root = Path(allure_report_dir).resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Allure report directory not found: {root}")

    nginx = _install_nginx_if_missing()
    if not nginx:
        os_name = _detect_os()
        msg = [
            "Nginx not found and could not auto-install.",
            "Please install it and re-run:",
        ]
        if os_name == "mac":
            msg.append("  brew install nginx")
        elif os_name == "linux":
            msg.append("  sudo apt install nginx    # (Debian/Ubuntu)")
            msg.append("  # or sudo dnf/yum install nginx  # (RHEL/CentOS/Fedora)")
        elif os_name == "windows":
            msg.append("  winget install Nginx.Nginx   # or install from nginx.org and add to PATH")
        raise RuntimeError("\n".join(msg))

    chosen_port = port if port else find_free_port()

    if prefer_system:
        # System mode: write a temporary site conf and ask user to include it manually,
        # OR advise to copy to their sites-enabled and reload (since paths vary widely).
        # We still produce a working user-local config to validate syntax before reload.
        prefix = Path(tempfile.mkdtemp(prefix="nrobo-nginx-"))
        conf_path = _write_user_local_conf(prefix, root, chosen_port)

        # Check config before reload (nginx -t)
        subprocess.run([nginx, "-t", "-p", str(prefix), "-c", str(conf_path)], check=True)

        # Try system reload (requires admin). User must have a server block listening on chosen_port or
        # adapt their system config accordingly. We surface the URL regardless.
        _reload_system_nginx()
        mode = "system"
        runtime_dir = str(prefix)
    else:
        # User-local isolated instance (recommended). No sudo, no system files.
        prefix = Path(tempfile.mkdtemp(prefix="nrobo-nginx-"))
        conf_path = _write_user_local_conf(prefix, root, chosen_port)
        # Validate then start/reload
        subprocess.run([nginx, "-t", "-p", str(prefix), "-c", str(conf_path)], check=True)
        _start_user_local_nginx(nginx, prefix, conf_path)
        mode = "user-local"
        runtime_dir = str(prefix)

    # Wait until socket is listening
    if not wait_until_listening(port=chosen_port, host="127.0.0.1", timeout=6):
        raise RuntimeError(f"Nginx didn’t start listening on port {chosen_port}.")

    url = f"http://localhost:{chosen_port}/"
    logger.info(f"📎 Allure report served at: {url}")

    if open_browser:
        try:
            import webbrowser

            webbrowser.open(url)
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")

    return NginxServeResult(
        url=url,
        port=chosen_port,
        root_dir=str(root),
        nginx_path=nginx,
        mode=mode,
        runtime_dir=runtime_dir,
    )


def stop_persisted_user_local_if_any() -> bool:
    state = load_state()
    if not state or state.get("mode") != "user-local":
        return False
    pid_file = Path(state["runtime_dir"]) / "logs" / "nginx.pid"
    if not pid_file.is_file():
        clear_state()
        return False
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 15)  # SIGTERM
        clear_state()
        logger.info("🛑 Stopped persisted user-local Nginx and cleared state.")
        return True
    except Exception as e:
        logger.warning(f"Unable to stop persisted Nginx: {e}")
        return False
