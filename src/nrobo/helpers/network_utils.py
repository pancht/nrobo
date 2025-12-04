"""
network_utils.py
----------------
Cross-platform utilities for handling networking and ports in nRoBo.

Provides:
    - find_free_port()   → Auto-detect a free TCP port
    - is_port_in_use()   → Check if a port is already in use
    - get_local_ip()     → Get the system's primary local IP
    - wait_for_port()    → Wait until a port becomes available
    - temporary_port()   → Context manager to reserve a port temporarily

Supported on Windows, macOS, and Linux.

Author: Panchdev Singh Chauhan
"""

import contextlib
import platform
import socket
import time
from typing import Optional

from nrobo.helpers.logging_helper import get_logger

logger = get_logger(name="network_utils")


def find_free_port() -> int:
    """
    Find an available TCP port in a cross-platform way.

    Uses the OS's ephemeral port allocation (port=0) which is safe on all
    major platforms.

    Returns:
        int: A free TCP port number
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            s.listen(1)
            port = s.getsockname()[1]
            logger.debug(f"[NetworkUtils] Found free port: {port}")
            return port
    except OSError as e:
        logger.error(f"❌ Failed to find free port: {e}")
        raise


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """
    Check if a TCP port is currently in use.

    Works across all platforms using non-blocking connection attempt.

    Args:
        port (int): Port number to check
        host (str): Host address, default '127.0.0.1'

    Returns:
        bool: True if port is occupied, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex((host, port))
        in_use = result == 0
        logger.debug(f"[NetworkUtils] Port {port} in use: {in_use}")
        return in_use


def wait_for_port(port: int, host: str = "127.0.0.1", timeout: int = 10) -> bool:
    """
    Wait until a port becomes available (not in use) or timeout occurs.

    Args:
        port (int): Port to check
        host (str): Hostname
        timeout (int): Seconds to wait

    Returns:
        bool: True if the port became available, False if timeout expired
    """
    start = time.time()
    while time.time() - start < timeout:
        if not is_port_in_use(port, host):
            logger.info(f"[NetworkUtils] Port {port} is now free ✅")
            return True
        time.sleep(0.5)
    logger.warning(f"[NetworkUtils] Port {port} still in use after {timeout}s ⚠️")
    return False


def wait_until_listening(port: int, host: str = "127.0.0.1", timeout: int = 10) -> bool:
    """
    Wait until a TCP port starts accepting connections (i.e., service listening).

    Args:
        port (int): Port number to check.
        host (str): Hostname or IP address.
        timeout (int): Seconds to wait before giving up.

    Returns:
        bool: True if service starts listening before timeout, False otherwise.
    """
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                logger.info(f"[NetworkUtils] Port {port} is now listening ✅")
                return True
        time.sleep(0.5)
    logger.warning(f"[NetworkUtils] Port {port} not listening after {timeout}s ⚠️")
    return False


def get_local_ip() -> Optional[str]:
    """
    Get the primary local IP address of the system.

    Works across Windows, macOS, and Linux.
    Returns None if not connected to any network.

    Returns:
        Optional[str]: Local IP (e.g., '192.168.1.100') or None
    """
    try:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            # connect() doesn't actually send packets
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            logger.debug(f"[NetworkUtils] Local IP detected: {local_ip}")
            return local_ip
    except Exception as e:
        logger.warning(f"[NetworkUtils] Unable to detect local IP: {e}")
        return None


@contextlib.contextmanager
def temporary_port():
    """
    Context manager that yields a temporary free port.
    Ensures it stays reserved while inside the context.

    Example:
        >>> with temporary_port() as port:
        >>>     start_server(port)
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    logger.debug(f"[NetworkUtils] Reserved temporary port: {port}")
    try:
        yield port
    finally:
        try:
            s.close()
            logger.debug(f"[NetworkUtils] Released temporary port: {port}")
        except Exception as e:
            logger.error(f"[NetworkUtils] Failed to close temp port: {e}")


def platform_info() -> str:
    """
    Return current OS and version information for logging/debugging.

    Example:
        'macOS 14.3 (arm64)' or 'Windows 11 (AMD64)'
    """
    return f"{platform.system()} {platform.release()} ({platform.machine()})"
