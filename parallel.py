import time
from multiprocessing import freeze_support

from pebble import concurrent, ProcessPool


#python -m pip install pebble

class TmpProc:

    @concurrent.thread
    def function(self, arg, kwarg=0):
        print ("arg is ", arg)
        time.sleep(arg)
        print ("slept now I am here", arg)
        return arg + kwarg

if __name__ == '__main__':
    #freeze_support()

    print "here I am"
    obj1 = TmpProc()
    obj2 = TmpProc()

    future1 = obj1.function(1, kwarg=1)
    future2 = obj2.function(2, kwarg=1)
    #future2 = TmpProc.function(obj2, 2, kwarg=1)

    print("resutl 2", future2.result())
    print("resutl 1",future1.result())



with ProcessPool() as pool:
    future = pool.map(function, 1,2, timeout=10)

    try:
        for n in future.result():
            print(n)
    except TimeoutError:
        print("TimeoutError: aborting remaining computations")
        future.cancel()