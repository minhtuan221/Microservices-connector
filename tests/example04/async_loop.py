from microservices_connector import spawn, Interservices as conn
import time
import asyncio
from datetime import datetime
friend = conn.Friend('1','10.26.53.142:5010')
import requests 
import concurrent.futures as fn

async def myTask(i):
    time.sleep(1)
    print("Processing Task %s" % i)


@spawn.async_to_sync
async def myTaskGenerator():
    for i in range(5):
        asyncio.ensure_future(myTask(i))

# myTaskGenerator()
async def call_api():
    r = requests.get('http://example.com/')
    print('request status is %s' % r.text)

# @spawn.async_to_sync
async def low_long_job(param):
    print('Long job %s begin' % param)
    await call_api()
    print('end %s'%param)
    return 'end'

# for i in range(100):
#     low_long_job(i)

# print('End of 100 long job')
tasks=[]
start = time.time()

# @spawn.sync_to_async
def do_async():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for i in range(10):
            tasks.append(asyncio.ensure_future(low_long_job(i)))
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
do_async()

print('This will out first')


# async def custom_sleep():
#     print('SLEEP {}\n'.format(datetime.now()))
#     await asyncio.sleep(1)


# async def factorial(name, number):
#     f = 1
#     for i in range(2, number+1):
#         print('Task {}: Compute factorial({})'.format(name, i))
#         await custom_sleep()
#         f *= i
#     print('Task {}: factorial({}) is {}\n'.format(name, number, f))


# loop = asyncio.get_event_loop()
# tasks = [
#     asyncio.ensure_future(factorial("A", 3)),
#     asyncio.ensure_future(factorial("B", 4)),
# ]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()
end = time.time()
print("Total time: {}".format(end - start))

