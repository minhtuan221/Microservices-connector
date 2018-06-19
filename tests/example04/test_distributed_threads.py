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
    # print('working on b=%s' % b)
    time.sleep(random.random())
    return 'working on b=%s' % b
    # return 5


def wait_on_a(a):
    # print('working on a=%s' % a)
    time.sleep(1)
    return a
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

def Print_out(q):
    while q:
        obj = q.get()
        print(obj)


def main():

    thread_out_queue = queue.Queue()
    pool = spawn.DistributedThreads(
        max_workers=4, max_watching=100, out_queue=thread_out_queue)

    start = time.time()
    for item in poll:
        pool.submit_id(item['id'], wait_on_a, item)
        # print(thread_out_queue.get())
    t = spawn.Worker(thread_out_queue, print)
    t.daemon = True
    t.start()
    for w in pool.worker_list:
        print(w.name)
    pool.shutdown()
    print('Finish after: ', time.time()-start, 'seconds')

    print("========= End of threads ==============")

    # process_out_queue = multiprocessing.Queue()
    # pool2 = spawn.DistributedProcess(
    #     max_workers=4, max_watching=100, out_queue=process_out_queue)
    # for item in poll:
    #     pool2.submit_id(item['id'], wait_on_a, item)
    # # process = Worker(process_out_queue, print)
    # # process.daemon = True
    # # process.start()
    # pool2.shutdown()

    print('Finish after: ', time.time()-start, 'seconds')


if __name__ == '__main__':
    main()
