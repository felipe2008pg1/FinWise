"""
In-memory security monitor.
Detects anomalous behavior and issues log alerts.

Limitation: in-memory — counters reset upon every Render redeploy.
For persistence, replace the dictionaries with Redis (when scaling).
"""
import time
from collections import defaultdict
from app.logger import security_logger

# ===== CONFIGURATIONS =====
MAX_LOGIN_FAILURES     = 10   # failures before issuing an alert
LOGIN_FAILURE_WINDOW   = 300  # 5-minute (second) window
MAX_ERRORS_PER_MINUTE  = 20   # 5xx errors before alerting
ERROR_WINDOW           = 60   # 1-minute window

# ===== State in Memory =====
# { ip: [(timestamp, ...), ...] }
_login_failures: dict = defaultdict(list)
_error_events:   list = []

def _cleanup_old(events: list, window: int) -> list:
    cutoff = time.monotonic() - window
    return [e for e in events if e > cutoff]

# ===== Login Failure Detection =====
def record_login_failure(ip: str, email: str):
    now = time.monotonic()
    _login_failures[ip] = _cleanup_old(_login_failures[ip], LOGIN_FAILURE_WINDOW)
    _login_failures[ip].append(now)

    count = len(_login_failures[ip])

    if count == MAX_LOGIN_FAILURES:
        security_logger.critical(
            f'ALERT_BRUTE_FORCE | ip={ip} | email={email} | '
            f'failures={count} | window={LOGIN_FAILURE_WINDOW}s | '
            f'action=consider_blocking'
        )
    elif count > MAX_LOGIN_FAILURES and count % 5 == 0:
        # Logs every 5 extra failures to avoid spam.
        security_logger.critical(
            f'ALERT_BRUTE_FORCE_CONTINUED | ip={ip} | email={email} | '
            f'failures={count} | window={LOGIN_FAILURE_WINDOW}s'
        )

def get_failure_count(ip: str) -> int:
    _login_failures[ip] = _cleanup_old(_login_failures[ip], LOGIN_FAILURE_WINDOW)
    return len(_login_failures[ip])

def clear_failures(ip: str):
    """Chamado após login bem-sucedido para resetar o contador do IP."""
    _login_failures.pop(ip, None)

# ===== ERROR SPIKE DETECTION =====
def record_error_event(path: str, status: int, ip: str):
    global _error_events
    now = time.monotonic()
    _error_events.append(now)
    _error_events = _cleanup_old(_error_events, ERROR_WINDOW)

    count = len(_error_events)
    if count == MAX_ERRORS_PER_MINUTE:
        security_logger.critical(
            f'ALERT_ERROR_SPIKE | errors={count} | window={ERROR_WINDOW}s | '
            f'last_path={path} | last_status={status} | last_ip={ip}'
        )

# ===== SUSPICIOUS IP DETECTION =====
def check_suspicious_ip(ip: str, path: str):
    """
Detects IPs that rapidly hit multiple sensitive endpoints.
    Hook for future integration with a blocklist or Cloudflare.
    """
    failure_count = get_failure_count(ip)
    if failure_count >= MAX_LOGIN_FAILURES:
        security_logger.warning(
            f'SUSPICIOUS_IP | ip={ip} | path={path} | '
            f'login_failures={failure_count} | '
            f'recommendation=block_ip'
        )
        return True
    return False
