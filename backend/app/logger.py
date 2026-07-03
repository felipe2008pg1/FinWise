import logging
import sys
from datetime import datetime, timezone

# Custom formatter with UTC timestamp and structured context
class SecurityFormatter(logging.Formatter):
    def format(self, record):
        record.utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        return super().format(record)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = SecurityFormatter(
            fmt='[%(utc_time)s] %(levelname)s [%(name)s] %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# Central security logger
security_logger = setup_logger('finwise.security')
app_logger = setup_logger('finwise.app')

def log_auth_success(user_id: str, email: str, ip: str):
    security_logger.info(f'AUTH_SUCCESS | user_id={user_id} | email={email} | ip={ip}')

def log_auth_failure(email: str, ip: str, reason: str):
    security_logger.warning(f'AUTH_FAILURE | email={email} | ip={ip} | reason={reason}')

def log_register(email: str, ip: str, success: bool):
    if success:
        security_logger.info(f'REGISTER_SUCCESS | email={email} | ip={ip}')
    else:
        security_logger.warning(f'REGISTER_FAILURE | email={email} | ip={ip}')

def log_rate_limit(ip: str, path: str):
    security_logger.warning(f'RATE_LIMIT_HIT | ip={ip} | path={path}')

def log_unauthorized(user_id: str, path: str, ip: str):
    security_logger.warning(f'UNAUTHORIZED_ACCESS | user_id={user_id} | path={path} | ip={ip}')

def log_internal_error(path: str, error_type: str, ip: str):
    security_logger.error(f'INTERNAL_ERROR | path={path} | error_type={error_type} | ip={ip}')

def log_jwt_expired(user_id: str, ip: str):
    security_logger.warning(f'JWT_EXPIRED | user_id={user_id} | ip={ip}')

def log_password_reset(email: str, ip: str):
    security_logger.info(f'PASSWORD_RESET_REQUESTED | email={email} | ip={ip}')
