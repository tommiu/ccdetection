'''
Created on Nov 10, 2015

Taken from 
http://www.grantjenks.com/wiki/random/python_multiprocessing_lazy_iterating_map
(2013/12/03 11:14 by grant)

and extended by me.

@author: Tommi Unruh
'''

import multiprocessing as mp
import Queue

class LazyMP(object):
    """
    Lazy multiprocessing class.
    """

    def __init__(self):
        '''
        Constructor
        '''
        
    def work(self, recvq, sendq):
        for _func, args in iter(recvq.get, None):
            result = _func(args)
            sendq.put(result)
    
    def poolImapUnordered(self, 
                    _func, _iterable, 
                    procs=mp.cpu_count(), 
                    custom_ids_object=None
                    ):
        sendq = mp.Queue(procs)
        recvq = mp.Queue()

        # Start processes.
        # Processes start working when they receive a task from the
        # receive queue.
        for _ in xrange(procs):
            mp.Process(target=self.work, args=(sendq, recvq)).start()
        
        # Iterate iterable and populate queues.
        send_len = 0
        recv_len = 0
        
        try:
            working_processes = 0
            while True:
                if working_processes < procs:
                    # There is a process not working at the moment.
                    # Give it a task.
                    working_processes += 1
                    
                    # Send new task to queue.
                    sendq.put((_func, _iterable.next()), True, 0.1)
                    send_len += 1
                else:
                    # Queue of new tasks is full,
                    # so work until a process finishes.
                    while True:
                        try:
                            # Wait for result of a process.
                            # In this case, the result is a custom id number,
                            # as returned by the function analyseData in
                            # main.py
                            result = recvq.get(False)
                            working_processes -= 1
                            
                            # If an object was passed for custom process IDs,
                            # we fill it up with the returned id from 'result'.
                            if custom_ids_object:
                                custom_ids_object.addToGenerator(result)
                                
                            recv_len += 1
                            yield result
                        except Queue.Empty:
                            break
                
        except StopIteration:
            # _iterable was consumed completely.
            pass
        
        # Collect remaining results.
        while recv_len < send_len:
            result = recvq.get()
            if custom_ids_object:
                custom_ids_object.addToGenerator(result)
                
            recv_len += 1
            yield result
            
        # Terminate worker processes.
        for _ in xrange(procs):
            sendq.put(None)
            
class ProcessIdGenerator(object):
    """
    Process number management.
    Allows a lazy multithreading pool to pass the correct process ID 
    for a waiting process.
    """
    def __init__(self):
        pass
    
    def getGenerator(self, ids):
        self.waiting_ids = mp.Queue(len(ids))
        for _id in ids:
            self.waiting_ids.put(int(_id))
            
        while True:
            # Raises IndexError on empty list.
            try:
                _next = int(self.waiting_ids.get())
                yield _next
            
            except:
                pass
    
    def addToGenerator(self, _id):
        self.waiting_ids.put(int(_id))
