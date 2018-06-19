from multiprocessing.pool import ThreadPool
from datetime import datetime
import time

def get_input():
  print(input())

pool = ThreadPool(processes=1)


while True:
  async_result = pool.apply_async(get_input, ()) # tuple of args for foo
  print(datetime.now())
  time.sleep(1)



