import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import deque
from queue import Queue
import threading
import random


def wait_on_b(b):
    time.sleep(random.random()*2)
    # b will never complete because it is waiting on a.
    print('working on b=%s' % b)
    return 5


def wait_on_a(a):
    time.sleep(1)
    # a will never complete because it is waiting on b.
    print('working on a=%s' % a)
    return 6


poll = [
    {'id': 1, 'x': 'Nguyen'},
    {'id': 1, 'x': 'Minh'},
    {'id': 1, 'x': 'Tuan'},
    {'id': 2, 'x': 'Vu'},
    {'id': 3, 'x': 'Ai do khac'},
    {'id': 2, 'x': 'Ngoc'},
    {'id': 2, 'x': 'Anh'},
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

    def __init__(self, queue, out_queue=None):
        """Threaded Async reader, read data from queue
        
        Arguments:
            queue {[type]} -- queue or deque
        
        Keyword Arguments:
            out_queue {[type]} -- queue receive result (default: {None})
        """

        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def input_function(self, f, *args, **kwargs):
        pass

    def output_function(self, f, *args, **kwargs):
        pass

    def run(self):
        while True:
            # Grabs host from queue
            f, args, kwargs = self.queue.get()

            # Grabs item and put to input_function
            self.input_function(f, args, kwargs)
            result = f(*args, **kwargs)
            self.output_function(f, args, kwargs)

            if self.out_queue is not None:
                self.out_queue.put(result)

            # Signals to queue job is done
            self.queue.task_done()

class DistributedThreads(object):
    
    def __init__(self, out_queue=None, max_workers=4, max_watching=100):
        self.out_queue = out_queue
        self.max_workers = max_workers
        self.max_watching = max_watching
        self.current_id = 0
        self.init_worker()
    
    def init_worker(self):
        # create list of queue
        self.queue_list = [Queue() for i in range(self.max_workers)]
        # create list of threads:
        self.worker_list = []
        for i in range(self.max_workers):
            one_worker = AsyncThread(self.queue_list[i], out_queue=self.out_queue)
            one_worker.daemon = True
            self.worker_list.append(one_worker)
            one_worker.start()
        # create list of watching queue
        self.watching_list = [deque() for i in range(self.max_workers)]
    
    def iterate_queue(self, watching:list, key):
        if key not in watching and key is not None:
            watching.append(key)
        if len(watching) > self.max_watching:
            watching.popleft()
            # print('pop one left', watching)
        
    def choose_worker(self):
        return (self.current_id+1)%self.max_workers
    
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
        print(worker_id, watching)
        # add function to queue
        worker.put((f, args, kwargs))

    def shutdown(self):
        for q in self.queue_list:
            q.join()
    

def main():
    start = time.time()
    pool = DistributedThreads(max_workers=10, max_watching=100)
    for item in poll:
        pool.submit(wait_on_a, item)
    for item in poll:
        pool.submit_id(item['id'], wait_on_b, item)
    pool.shutdown()
    print('Finish after: ', time.time()-start, 'seconds')
    print('Acitve Thread is:', threading.active_count())

if __name__ == '__main__':
    main()
