from pebble import concurrent

@concurrent.process
def function(arg, kwarg=0):
    return arg + kwarg

future = function(1, kwarg=1)

print(future.result())

#python -m pip install pebble