import time
from threading import Lock, Thread, current_thread


class TokenBucketFilter:
    def __init__(self, max_tokens, refill_rate_s):
        self.max_tokens = max_tokens
        self.refill_rate_s = refill_rate_s
        self.last_release_time = time.time()
        self.tokens = 0
        self.lock = Lock()

    def get_token(self):
        with self.lock:
            self.tokens = min(
                self.max_tokens,
                self.tokens
                + int((time.time() - self.last_release_time) / self.refill_rate_s),
            )
            # Assume refill rate is at least 1/s
            if self.tokens <= 0:
                time.sleep(1)
            else:
                self.tokens -= 1
            self.last_release_time = time.time()

            print(
                f"[{current_thread().getName()}@{time.strftime('%T')}] released a token"
            )


def main():
    tbf = TokenBucketFilter(5, 1)
    time.sleep(3)
    threads = [Thread(name=f"Token-{i}", target=tbf.get_token) for i in range(1, 11)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
