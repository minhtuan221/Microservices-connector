# import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import deque
import queue
import threading
import multiprocessing
import random
import time
import spawn

def wait_on_b(b):
    time.sleep(random.random())
    # b will never complete because it is waiting on a.
    print('working on b=%s' % b)
    return 'working on b=%s' % b
    # return 5


def wait_on_a(a):
    time.sleep(1)
    # a will never complete because it is waiting on b.
    return 'working on a=%s' % a
    # return 6


poll = [
    {'id': 1, 'x': 'Nguyen'},
    {'id': 1, 'x': 'Minh'},
    {'id': 1, 'x': 'Tuan'},
    {'id': 2, 'x': 'Vu'},
    {'id': 3, 'x': 'Ai do khac'},
    {'id': 2, 'x': 'Kim'},
    {'id': 2, 'x': 'Oanh'},
    {'id': 4, 'x': '1'},
    {'id': 4, 'x': '2'},
    {'id': 4, 'x': '3'},
    {'id': 4, 'x': '4'},
    {'id': 4, 'x': '5'},
    {'id': 4, 'x': '6'},
    {'id': 4, 'x': '7'},
    {'id': 4, 'x': '8'},
    {'id': 5, 'x': '101'},
    {'id': 5, 'x': '102'},
    {'id': 5, 'x': '103'},
    {'id': 5, 'x': '104'},
    {'id': 5, 'x': '105'},
    {'id': 6, 'x': 'Test watching'},
    {'id': 6, 'x': 'Test watching'},
    {'id': 7, 'x': 'Test watching'},
    {'id': 8, 'x': 'Test watching'},
    {'id': 9, 'x': 'Test watching'},
    {'id': 10, 'x': 'Test watching'},
    {'id': 11, 'x': 'Test watching'},
    {'id': 12, 'x': 'Test watching'},
    {'id': 13, 'x': 'Test watching'},
    {'id': 14, 'x': 'Test watching'},
    {'id': 15, 'x': 'Test watching'},
    {'id': 16, 'x': 'Test watching'},
    {'id': 17, 'x': 'Test watching'},
    {'id': 18, 'x': 'Test watching'},
    {'id': 19, 'x': 'Test watching'},
    {'id': 20, 'x': 'Test watching'},
    {'id': 21, 'x': 'Test watching'},
    {'id': 22, 'x': 'Test watching'},
]


class AsyncThread(threading.Thread):
    """Threaded Async reader, read data from queue"""

    def __init__(self, in_queue, out_queue=None):
        """Threaded Async reader, read data from queue

        Arguments:
            queue {[type]} -- queue or deque

        Keyword Arguments:
            out_queue {[type]} -- queue receive result (default: {None})
        """

        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            # Grabs host from queue
            f, args, kwargs = self.in_queue.get()

            # Grabs item and put to input_function
            result = f(*args, **kwargs), None
            result = result[:-1]

            if self.out_queue is not None:
                self.out_queue.put(*result)

            # Signals to queue job is done
            self.in_queue.task_done()


class AsyncProcess(multiprocessing.Process):

    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            # Grabs host from queue
            f, args, kwargs = self.in_queue.get()

            # Grabs item and put to input_function
            result = f(*args, **kwargs), None
            result = result[:-1]

            if self.out_queue is not None:
                self.out_queue.put(*result)

            # Signals to queue job is done
            self.in_queue.task_done()
            if self.stop_event.is_set():
                print('Process %s is stopping' % self.pid)
                break


class DistributedThreads(object):

    def __init__(self, out_queue=None, max_workers=4, max_watching=100):
        self.out_queue = out_queue
        self.max_workers = max_workers
        self.max_watching = max_watching
        self.current_id = 0
        self.init_worker()

    def init_worker(self):
        # create list of queue
        self.queue_list = [queue.Queue() for i in range(self.max_workers)]
        # create list of threads:
        self.worker_list = []
        for i in range(self.max_workers):
            one_worker = AsyncThread(
                self.queue_list[i], out_queue=self.out_queue)
            one_worker.daemon = True
            self.worker_list.append(one_worker)
            one_worker.start()
        # create list of watching queue
        self.watching_list = [deque() for i in range(self.max_workers)]

    def iterate_queue(self, watching: list, key):
        if key not in watching and key is not None:
            watching.append(key)
        if len(watching) > self.max_watching:
            watching.popleft()
            # print('pop one left', watching)

    def choose_worker(self):
        return (self.current_id+1) % self.max_workers

    def submit(self, f, *args, **kwargs):
        return self.submit_id(None, f, *args, **kwargs)

    def submit_id(self, key, f, *args, **kwargs):
        worker_id = None
        # check if key belong to any worker
        if key is not None:
            for i in range(self.max_workers):
                if key in self.watching_list[i]:
                    if worker_id is not None:
                        raise ValueError("Key belong to more than one worker")
                    worker_id = i
                    self.current_id = worker_id
                    break
        # choosing a work_id if not
        if worker_id is None:
            worker_id = self.choose_worker()
            # print('choose queue =>', worker_id)
            self.current_id = worker_id
        # assign to worker and watching list
        worker = self.queue_list[worker_id]
        watching = self.watching_list[worker_id]

        # add key to a watching
        self.iterate_queue(watching, key)
        # print(worker_id, watching)
        # add function to queue
        worker.put((f, args, kwargs))

    def shutdown(self):
        for q in self.queue_list:
            q.join()


class DistributedProcess(DistributedThreads):
    def init_worker(self):
        # create list of queue
        self.queue_list = [multiprocessing.JoinableQueue()
                           for i in range(self.max_workers)]
        # create list of threads:
        self.worker_list = []
        for i in range(self.max_workers):
            one_worker = AsyncProcess(
                self.queue_list[i], out_queue=self.out_queue)
            self.worker_list.append(one_worker)
            one_worker.start()
        # create list of watching queue
        self.watching_list = [deque() for i in range(self.max_workers)]

    def shutdown(self):
        for q in self.queue_list:
            q.join()
        for process in self.worker_list:
            print('Process %s is stopping' % process.pid)
            process.terminate()


class Worker(threading.Thread):
    """Threaded title parser"""

    def __init__(self, out_queue, f):
        threading.Thread.__init__(self)
        self.out_queue = out_queue
        self.f = f

    def run(self):
        while True:
            # Grabs chunk from queue
            args = self.out_queue.get(), None

            # Parse the chunk
            args = args[:-1]
            self.f(*args)

            # Signals to queue job is done
            self.out_queue.task_done()


def Print_out(q):
    while q:
        obj = q.get()
        print(obj)


def main():
    start = time.time()

    thread_out_queue = queue.Queue()
    pool = spawn.DistributedThreads(
        max_workers=4, max_watching=100, out_queue=thread_out_queue)
    for item in poll:
        pool.submit_id(item['id'], wait_on_a, item)
        # print(thread_out_queue.get())
    t = spawn.Worker(thread_out_queue, print)
    t.daemon = True
    t.start()
    pool.shutdown()
    print('Finish after: ', time.time()-start, 'seconds')

    print("========= End of threads ==============")

    process_out_queue = multiprocessing.Queue()
    pool2 = spawn.DistributedProcess(
        max_workers=4, max_watching=100, out_queue=process_out_queue)
    for item in poll:
        pool2.submit_id(item['id'], wait_on_b, item)
    # process = Worker(process_out_queue, print)
    # process.daemon = True
    # process.start()
    pool2.shutdown()

    print('Finish after: ', time.time()-start, 'seconds')


if __name__ == '__main__':
    main()
