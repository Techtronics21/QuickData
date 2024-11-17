import time
from threading import Lock


class RateLimiter:
    def __init__(self, rate: int, per: int = 60):
        self.rate = rate  # Number of requests
        self.per = per  # Per X seconds
        self.tokens = rate
        self.last_update = time.time()
        self.lock = Lock()

    def _add_tokens(self):
        now = time.time()
        time_passed = now - self.last_update
        new_tokens = time_passed * (self.rate / self.per)
        self.tokens = min(self.rate, self.tokens + new_tokens)
        self.last_update = now

    def acquire(self):
        with self.lock:
            self._add_tokens()
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    def wait(self):
        while not self.acquire():
            time.sleep(0.1)
