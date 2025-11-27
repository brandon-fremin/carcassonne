from typing import Any, Callable
import time, hashlib, json
import functools, logging, traceback
from threading import RLock, Lock


logger = logging.getLogger(__name__)


__synchronized_impl_lock = Lock()
def synchronized(func: Callable):
    lock_name = "__synchronized_impl_lock"
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, lock_name):  # relies on GIL
            with __synchronized_impl_lock:
                if not hasattr(self, lock_name):
                    setattr(self, lock_name, RLock())
        lock: RLock = getattr(self, lock_name)
        timeout = 10
        try:
            lock.acquire(timeout=timeout)
            return func(self, *args, **kwargs)
        except TimeoutError as e:
            logging.error(f"Failed to acquire synchronization lock after {timeout} seconds: {e}\n traceback={traceback.format_exc()}")
        finally:
            lock.release()
        return func(self, *args, **kwargs)
    return wrapper


def to_json(obj: Any):
    if isinstance(obj, list):
        return [to_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k:to_json(v) for k,v in obj.items()}
    elif isinstance(obj, bytes):
        # return base64.b64encode(obj).decode("utf-8")
        return f"<blob {len(obj)}B>"
    return obj


def truncate(s: str, max_length: int) -> str:
    if len(s) <= max_length:
        return s
    tail = f" ... [shortned from {len(s)} chars]"
    return s[:max_length-len(tail)] + tail


def http_timer(func: Callable):
    max_len = 250
    cyan = '\033[96m'
    reset = '\033[0m'
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.info(f"func={cyan}{func.__name__}{reset} args={truncate(str(args), max_len)} kwargs={truncate(str(kwargs), max_len)}")
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"func={cyan}{func.__name__}{reset} result={truncate(str(result), max_len)} elapsedSec={cyan}{duration:.3f}{reset}")
        return result
    return wrapper


def hash(s: dict | list | str | bytes | int, max_length: int = 16) -> str:
    if isinstance(s, dict) or isinstance(s, list):
        s = json.dumps(s, sort_keys=True)
    if isinstance(s, int):
        s = str(s)
    if isinstance(s, str):
        s = s.encode('utf-8')
    if not isinstance(s, bytes):
        raise ValueError(f"Cannot hash object of type {type(s)}")
    h = hashlib.sha256(s).hexdigest()
    return h[:min(max_length, len(h))]