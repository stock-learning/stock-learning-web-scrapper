
def retry(times, iter_message='', except_message=''):
    def tryIt(func, *fargs, **fkwargs):
        def f(*fargs, **fkwargs):
            attempts = 0
            while attempts < times:
                try:
                    print(iter_message.format((attempts + 1), *fargs, **fkwargs))
                    return func(*fargs, **fkwargs)
                except Exception as e:
                    print(except_message.format(*fargs, **fkwargs))
                    print(e)
                    attempts += 1
        return f
    return tryIt
