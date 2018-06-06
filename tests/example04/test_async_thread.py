import threading
import time
import queue

import random


class AsyncThread(threading.Thread):
    """Threaded website reader"""

    def __init__(self, queue, f):
        threading.Thread.__init__(self)
        self.queue = queue
        self.f = f

    def run(self):
        while True:
            # Grabs host from queue
            host = self.queue.get()

            # Grabs urls of hosts and then grabs chunk of webpage
            self.f(host)
            print("Reading: %s" % host)

            # Signals to queue job is done
            self.queue.task_done()


queue = queue.Queue()
threads =[]
def test(item):
    print('item is:',item)
for i in range(5):
    t = AsyncThread(queue, test)
    t.daemon = True
    threads.append(t)
    t.start()
hosts = [i for i in range(20)]
# Populate queue with data
for host in hosts:
    queue.put(host)
# Wait on the queue until everything has been processed
queue.join()
