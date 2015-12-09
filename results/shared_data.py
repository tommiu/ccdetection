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
    KEY_CLONES  = "clones"
    KEY_COUNTER = "counter"
    KEY_QUERY_TIME = "query_time_total"
    KEY_FIRST_COUNTER = "first_query_counter"
    KEY_PROJECTS_COUNTER = "projects_counter"
    KEY_FIRST_QUERY_TIME = "first_query_time_total"

    def __init__(self, path):
        """
        Setup all values to be shared (between processes) values.
        """
        self.path = path
        self.clones = Manager().list()
        self.counter = Value("i", 0)
        self.nodes_total = Value("i", 0)            
        self.first_counter = Value("i", 0)
        self.query_time_total = Value("d", 0)
        self.projects_counter = Value("i", 0)
        self.first_query_time_total = Value("d", 0)
        
        if os.path.isfile(path):
            self.loadData()
    
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
        self.clones  = Manager().list(data[self.KEY_CLONES])
        self.counter = Value("i", data[self.KEY_COUNTER])
        self.nodes_total = Value("i", data[self.KEY_NODES])
        self.first_counter = Value("i", data[self.KEY_FIRST_COUNTER])
        self.query_time_total = Value("d", data[self.KEY_QUERY_TIME])
        self.projects_counter = Value("i", data[self.KEY_PROJECTS_COUNTER])
        self.first_query_time_total = Value("d", data[self.KEY_FIRST_QUERY_TIME])
            
    def saveData(self):
        data = {}
        data[self.KEY_NODES]   = self.nodes_total.value
        data[self.KEY_CLONES] = []
        for clone in self.clones:
            data[self.KEY_CLONES].append(clone)
        data[self.KEY_COUNTER] = self.counter.value
        data[self.KEY_QUERY_TIME] = self.query_time_total.value 
        data[self.KEY_FIRST_COUNTER] = self.first_counter.value
        data[self.KEY_PROJECTS_COUNTER] = self.projects_counter.value
        data[self.KEY_FIRST_QUERY_TIME] = self.first_query_time_total.value
        
        with open(self.path, "wb") as fh:
            pickle.dump(data, fh, pickle.HIGHEST_PROTOCOL)

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