import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import deque
from queue import Queue
import threading
import random

def wait_on_b(b):
    time.sleep(random.random())
    print('working on b=%s'%b)  # b will never complete because it is waiting on a.
    return 5


def wait_on_a(a):
    time.sleep(1)
    print('working on a=%s'%a)  # a will never complete because it is waiting on b.
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
    {'id': 3, 'x': '5'},
    {'id': 3, 'x': '6'},
    {'id': 3, 'x': '7'},
    {'id': 3, 'x': '8'},
    {'id': 3, 'x': '9'},
    ]


class AsyncThread(threading.Thread):
    """Threaded website reader"""

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def input_function(self, parameter_list):
        pass

    def run(self):
        while True:
            # Grabs host from queue
            item = self.queue.get()

            # Grabs item and put to input_function
            self.input_function(item)

            # Signals to queue job is done
            self.queue.task_done()

class WaitGroup(object):
    def __init__(self, max_workers=4, max_watching=4):
        self.max_workers = max_workers
        self.max_watching = max_watching
        # 1=> create a watching list
        self.pending = deque([])
        self.watching = deque([])
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        # self.f = f
        # create a thread for doing sychonous job
        self.cleaner = ThreadPoolExecutor(max_workers=1)
        # self.cleaner = AsyncThread(self.pending)
        # self.cleaner.input_function = f
        # self.cleaner.daemon = True
        # self.cleaner.start()
        
    def clear_pending(self, f):
        if len(self.pending) > 0:
            for item in self.pending:
                if item['id'] not in self.watching:
                    f(item)
                    self.pending.remove(item)
            # self.pending.clear()
        # pass
    
    # def clean(self, item):
    #     self.pending.put(item)

    def execute_next(self, f, key, item):
        self.watching.append(key)  # append item['id'] to watching
        future = self.executor.submit(f, item)
        # remove one old item from watching if it's full

        # if future.done():
        if len(self.watching) > self.max_watching:
            self.watching.popleft()
        
    def submit(self, f, key, item):
        # forever going execute pool
        # 2=> check if the next item have same id in watching list
        print('watching', self.watching, (self.max_watching))
        if key in self.watching:
            # if yes => put this item in to a pending queue
            self.pending.append(item)
            # print('Synchonous', item, self.pending)
            # pending queue will be process in a single process with order and concurrent
        else:
            # then execute for the next item
            self.clear_pending(f)
            # print('==> Asynchonous', item, self.watching)
            self.execute_next(f, key, item)

    def clear(self, f):
        if len(self.pending) > 0:
            for item in self.pending:
                f(item)
            # self.pending.clear()  # clear pending after do
    
    def shutdown(self):
        # self.cleaner.join()
        self.cleaner.shutdown()
        self.executor.shutdown()

# start = time.time()
# print('Apply with normal ThreadPoolExecutor:')
# with ThreadPoolExecutor(max_workers=4) as e:
#     for item in poll:
#         e.submit(wait_on_b, item)
# print('Finish after: ',time.time()-start, 'seconds')

start = time.time()
print('Apply with WaitGroup:', len(poll))
e = WaitGroup(max_watching=2)
for item in poll:
    e.submit(wait_on_b, item['id'], item)
e.clear(wait_on_b)
# e.submit(wait_on_b,'0','end')
print(e.pending)
e.shutdown()
print('Finish after: ', time.time()-start, 'seconds')

a=deque([1,2,3,4])
a.popleft()
print(a)

# print('assign to %s'%i)
# # e.map(wait_on_a,[i for i in range(10,20)])

# never shutdown thread pool
# executor = ThreadPoolExecutor(max_workers=3)
# task1 = executor.submit(wait_on_b, 100)
# task2 = executor.submit(wait_on_b, 200)
