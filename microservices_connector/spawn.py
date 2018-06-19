import asyncio
import functools
import os
import threading
from concurrent.futures import Future, ThreadPoolExecutor

# Alternatively, you can create an instance of the loop manually, using:

import uvloop
# loop = uvloop.new_event_loop()
# asyncio.set_event_loop(loop)
import queue
import time
from collections import deque
import queue
import threading
import random
import multiprocessing


class SyncThread(threading.Thread):
    """Threaded Sync reader, read data from queue"""

    def __init__(self, in_queue, out_queue=None, name=None, watching: deque=None):
        """Threaded Sync reader, read data from queue

        Arguments:
            queue {[type]} -- queue or deque

        Keyword Arguments:
            out_queue {[type]} -- queue receive result (default: {None})
        """

        threading.Thread.__init__(self, name=name)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.watching = watching

    def main_process(self, f, *args, **kwargs):
        return f(*args, **kwargs)

    def run(self):
        while True:
            # Grabs host from queue
            f, args, kwargs = self.in_queue.get()

            # Grabs item and put to input_function
            result = self.main_process(f, *args, *kwargs), None
            result = result[:-1]

            if self.out_queue is not None:
                self.out_queue.put(*result)

            if self.watching is not None:
                self.watching.popleft()
                # print('Watching list is:', self.watching)

            # Signals to queue job is done
            self.in_queue.task_done()


class AsyncProcess(multiprocessing.Process):

    def __init__(self, in_queue, out_queue, name=None, watching: deque=None):
        multiprocessing.Process.__init__(self, name=name)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.stop_event = multiprocessing.Event()
        self.watching = watching

    def stop(self):
        self.stop_event.set()

    def main_process(self, f, *args, **kwargs):
        return f(*args, **kwargs)

    def run(self):
        while not self.stop_event.is_set():
            # Grabs host from queue
            f, args, kwargs = self.in_queue.get()

            # Grabs item and put to input_function
            result = self.main_process(f, *args, *kwargs), None
            result = result[:-1]

            if self.out_queue is not None:
                self.out_queue.put(*result)

            if self.watching is not None:
                self.watching.popleft()

            # Signals to queue job is done
            self.in_queue.task_done()
            if self.stop_event.is_set():
                print('Process %s is stopping' % self.pid)
                break


class DistributedThreads(object):

    def __init__(self, out_queue=None, max_workers=4, max_watching=100, worker=None, maxsize=0, delay=1):
        self.out_queue = out_queue
        self.max_workers = max_workers
        self.max_watching = max_watching
        self.current_id = 0
        self.max_qsize = maxsize
        self.delay = delay
        if worker is None:
            self.init_worker()
        else:
            self.init_worker(worker=worker)

    def init_worker(self, worker=SyncThread):
        # create list of queue
        self.queue_list = [queue.Queue(maxsize=self.max_qsize)
                           for i in range(self.max_workers)]

        # create list of watching queue
        self.watching_list = [deque() for i in range(self.max_workers)]

        # create list of threads:
        self.worker_list = []
        for i in range(self.max_workers):
            one_worker = worker(
                self.queue_list[i], out_queue=self.out_queue, name=str(i), watching=self.watching_list[i])
            one_worker.daemon = True
            self.worker_list.append(one_worker)
            one_worker.start()

    def iterate_queue(self, watching: list, key):
        if key is not None:
            watching.append(key)
        if len(watching) > self.max_watching:
            time.sleep(self.delay)

    def next_worker(self, last_id):
        return (last_id+1) % self.max_workers

    def check_next_queue(self, current_queue_size, last_id):
        next_id = self.next_worker(last_id)
        if current_queue_size >= self.queue_list[next_id].qsize():
            return next_id
        else:
            return self.check_next_queue(current_queue_size, next_id)

    def choose_worker(self):
        current_queue_size = self.queue_list[self.current_id].qsize()
        return self.check_next_queue(current_queue_size, self.current_id)
        # return (self.current_id+1) % self.max_workers

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
    def init_worker(self, worker=AsyncProcess):
        # create list of queue
        self.queue_list = [multiprocessing.JoinableQueue()
                           for i in range(self.max_workers)]

        # create list of watching queue
        self.watching_list = [deque() for i in range(self.max_workers)]

        # create list of threads:
        self.worker_list = []
        for i in range(self.max_workers):
            one_worker = worker(
                self.queue_list[i], out_queue=self.out_queue, name=str(i))
            self.worker_list.append(one_worker)
            one_worker.start()

    def iterate_queue(self, watching: list, key):
        if key is not None:
            watching.append(key)
        if len(watching) > self.max_watching:
            watching.popleft()

    def choose_worker(self):
        return (self.current_id+1) % self.max_workers

    def shutdown(self):
        for q in self.queue_list:
            q.join()
        for process in self.worker_list:
            print('Distributed Process %s is stopping' % process.pid)
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


class AsyncToSync:
    """
    Utility class which turns an awaitable that only works on the thread with
    the event loop into a synchronous callable that works in a subthread.
    Must be initialised from the main thread.
    """

    def __init__(self, awaitable):
        self.awaitable = awaitable
        self.uvloop = False
        try:
            self.main_event_loop = asyncio.get_event_loop()
        except RuntimeError:
            # There's no event loop in this thread. Look for the threadlocal if
            # we're inside SyncToAsync
            self.main_event_loop = getattr(
                SyncToAsync.threadlocal, "main_event_loop", None)

    def __call__(self, *args, **kwargs):
        # You can't call AsyncToSync from a thread with a running event loop
        try:
            event_loop = asyncio.get_event_loop()
        except RuntimeError:
            pass
        else:
            if event_loop.is_running():
                raise RuntimeError(
                    "You cannot use AsyncToSync in the same thread as an async event loop - "
                    "just await the async function directly."
                )
        # Make a future for the return information
        call_result = Future()
        # Use call_soon_threadsafe to schedule a synchronous callback on the
        # main event loop's thread
        if not (self.main_event_loop and self.main_event_loop.is_running()):
            # Make our own event loop and run inside that.
            if self.uvloop:
                loop = uvloop.new_event_loop()
            else:
                loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    self.main_wrap(args, kwargs, call_result))
            finally:
                try:
                    if hasattr(loop, "shutdown_asyncgens"):
                        loop.run_until_complete(loop.shutdown_asyncgens())
                finally:
                    loop.close()
                    asyncio.set_event_loop(self.main_event_loop)
        else:
            self.main_event_loop.call_soon_threadsafe(
                self.main_event_loop.create_task,
                self.main_wrap(
                    args,
                    kwargs,
                    call_result,
                ),
            )
        # Wait for results from the future.
        return call_result.result()

    def __get__(self, parent, objtype):
        """
        Include self for methods
        """
        return functools.partial(self.__call__, parent)

    async def main_wrap(self, args, kwargs, call_result):
        """
        Wraps the awaitable with something that puts the result into the
        result/exception future.
        """
        try:
            result = await self.awaitable(*args, **kwargs)
        except Exception as e:
            call_result.set_exception(e)
        else:
            call_result.set_result(result)


class SyncToAsync:
    """
    Utility class which turns a synchronous callable into an awaitable that
    runs in a threadpool. It also sets a threadlocal inside the thread so
    calls to AsyncToSync can escape it.
    """

    threadpool = ThreadPoolExecutor(
        max_workers=(
            int(os.environ["ASGI_THREADS"])
            if "ASGI_THREADS" in os.environ
            else None
        )
    )
    threadlocal = threading.local()

    def __init__(self, func):
        self.func = func

    async def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            self.threadpool,
            functools.partial(self.thread_handler, loop, *args, **kwargs),
        )
        return await asyncio.wait_for(future, timeout=None)

    def __get__(self, parent, objtype):
        """
        Include self for methods
        """
        return functools.partial(self.__call__, parent)

    def thread_handler(self, loop, *args, **kwargs):
        """
        Wraps the sync application with exception handling.
        """
        # Set the threadlocal for AsyncToSync
        self.threadlocal.main_event_loop = loop
        # Run the function
        return self.func(*args, **kwargs)


# Lowercase is more sensible for most things
sync_to_async = SyncToAsync
async_to_sync = AsyncToSync
