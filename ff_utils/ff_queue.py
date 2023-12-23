import queue


class LimitedQueue(queue.Queue):
    def __init__(self, maxsize=20):
        super().__init__(maxsize=maxsize)

    def put(self, item, block=True, timeout=None):
        # Override put method to release the oldest item if the queue is full
        if self.full():
            self.get_nowait()
        super().put(item, block, timeout)

    def get_values(self):
        return self.queue

