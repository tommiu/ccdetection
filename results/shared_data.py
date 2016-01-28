'''
Created on Dec 7, 2015

@author: Tommi Unruh
'''
import os
import cPickle as pickle
from multiprocessing import Value, Manager

class SharedData(object):
    """
    Handles shared statistical data, which we want to collect over several
    executions of the ccdetection tool.
    Only shared values are used, so that multiple child processes 
    can manipulate them.
    """

    KEY_NODES   = "nodes_total"
    KEY_INPATH  = "in_path"
    KEY_CLONES  = "clones"
    KEY_COUNTER = "counter"
    KEY_QUERY_TIME = "query_time_total"
    KEY_FIRST_COUNTER = "first_query_counter"
    KEY_PROJECTS_COUNTER = "projects_counter"
    KEY_FIRST_QUERY_TIME = "first_query_time_total"

    def __init__(self, path, lock, in_path=None):
        """
        Setup all values to be shared (between processes) values.
        """
        self.lock = lock
        self.path = path
        
        if os.path.isfile(path):
            self.loadData()
            
        else:
            self.in_path = in_path
            self.clones = Manager().list()
            self.counter = Value("i", 0)
            self.nodes_total = Value("i", 0)            
            self.first_counter = Value("i", 0)
            self.query_time_total = Value("d", 0)
            self.projects_counter = Value("i", 0)
            self.first_query_time_total = Value("d", 0)
    
    def incProjectsCounter(self):
        """
        Increase the counter of projects analysed.
        """
        self.projects_counter.value += 1
    
    def addQuery(self, query_time, first=False):
        """
        Add the statistical data of a query that did not find a code clone.
        """
        if first:
            self.first_counter.value += 1
            self.first_query_time_total.value += query_time
             
        else:
            self.counter.value += 1
            self.query_time_total.value += query_time
            
    def addFoundCodeClone(self, code_clone_data, first=False):
        """
        Add the statistical data of a query that did find a code clone.
        """
        self.addQuery(code_clone_data.getQueryTime(), first)
        self.clones.append(code_clone_data)
        
    def loadData(self):
        with open(self.path, "rb") as fh:
            data = pickle.load(fh)
            
        # Restore state from load data.
        self.in_path = data[self.KEY_INPATH]
        self.clones  = Manager().list(data[self.KEY_CLONES])
        self.counter = Value("i", data[self.KEY_COUNTER])
        self.nodes_total = Value("i", data[self.KEY_NODES])
        self.first_counter = Value("i", data[self.KEY_FIRST_COUNTER])
        self.query_time_total = Value("d", data[self.KEY_QUERY_TIME])
        self.projects_counter = Value("i", data[self.KEY_PROJECTS_COUNTER])
        self.first_query_time_total = Value("d", data[self.KEY_FIRST_QUERY_TIME])
            
    def saveData(self, queries, code_clones):
        """
        Save the data of an analysed project to file.
        To avoid conflicts of multiple processes adding and saving data
        at the same time, we save all data atomically and using a lock, which
        prevents multiple executions at once.
        """
        self.lock.acquire()
        # Increase projects counter.
        self.incProjectsCounter()    
        
        
        # Add all query data.
        for query_dict in queries:
            self.addQuery(query_dict["query_time"], query_dict["first"])

        # Add all data from found code clones
        for clone_dict in code_clones:
            self.addFoundCodeClone(clone_dict["clone"], clone_dict["first"])
        
        self.saveToFile(self.path)
        
        self.lock.release()

    def __str__(self):
        try:
            avg_query_time_nofirst = (self.query_time_total.value/
                                      float(self.counter.value))
        except:
            avg_query_time_nofirst = 0
            
        try:
            avg_query_time = (
                    (self.query_time_total.value + self.first_query_time_total.value)/
                    float(self.counter.value + self.first_counter.value)
                    )
            
        except:
            avg_query_time = 0

        try:
            avg_first_query_time = (self.first_query_time_total.value/
                                    float(self.first_counter.value))
        except:
            avg_first_query_time = 0 
                    
        try:
            avg_nodes = self.nodes_total.value/float(self.counter.value)
        except:
            avg_nodes = 0
        
        data = (
            "Projects analysed: %d\n"
            "Total queries executed: %d\n"
            "Average query time: %fs\n"
            "Average query time (without first query): %fs\n"
            "Average query time (first query only): %fs\n"
            "Average number of nodes in AST: %f\n"
            "Code clones found: %d"
            ) % (
                self.projects_counter.value,
                self.counter.value + self.first_counter.value, avg_query_time,
                avg_query_time_nofirst,
                avg_first_query_time,
                avg_nodes, len(self.clones)
                )
            
        return data
    
    def combineWith(self, shared_data):
        self.lock.acquire() 
        
        # Add the data of shared_data to this file.
        self.in_path = shared_data.in_path
        self.nodes_total.value += shared_data.nodes_total.value
        
        for clone in shared_data.clones:
            self.clones.append(clone)
            
        self.counter.value += shared_data.counter.value
        self.query_time_total.value += shared_data.query_time_total.value 
        self.first_counter.value += shared_data.first_counter.value
        self.projects_counter.value += shared_data.projects_counter.value
        self.first_query_time_total.value += (
                                    shared_data.first_query_time_total.value
                                    )
        
        self.lock.release()
        
    def saveToFile(self, out_file):
        # Transform data to dictionary for easy pickling.
        data = {}
        data[self.KEY_INPATH] = self.in_path
        data[self.KEY_NODES]  = self.nodes_total.value
        data[self.KEY_CLONES] = []
        for clone in self.clones:
            data[self.KEY_CLONES].append(clone)
        data[self.KEY_COUNTER] = self.counter.value
        data[self.KEY_QUERY_TIME] = self.query_time_total.value 
        data[self.KEY_FIRST_COUNTER] = self.first_counter.value
        data[self.KEY_PROJECTS_COUNTER] = self.projects_counter.value
        data[self.KEY_FIRST_QUERY_TIME] = self.first_query_time_total.value
        
        # Save data to file.
        with open(out_file, "wb") as fh:
            pickle.dump(data, fh, pickle.HIGHEST_PROTOCOL)
    
    def getClones(self):
        clones = []
        for clone in self.clones:
            clones.append(clone)
            
        return clones
    
    def getProjectsCount(self):
        return self.projects_counter.value

    def getInPath(self):
        return self.in_path
    
    def setInPath(self, path):
        self.in_path = path