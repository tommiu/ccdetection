'''
Created on Dec 8, 2015

@author: tommi
'''
import StringIO

class CodeCloneData(object):
    """
    Class to save and analyse the output of the ccdetection search.
    """


    def __init__(self, path="", query_path="", ln_start=-1, ln_end=-1, query_time=-1):
        '''
        Constructor
        '''
        self.path = path
        self.ln_end = ln_end
        self.ln_start = ln_start
        self.query_time = query_time
        self.query_path = query_path
        
    def stripDataFromOutput(self, output):
        """
        Extract the data from the ccdetection search output.
        Example output for a found code clone looks like this:
        
        Found a code clone on lines x to y
        File: filepath
        
        """
        buf = StringIO.StringIO(output)
        
        # Extract start and end linenumbers from first line.
        start_index = len("Found a code clone on lines ")
        ln_start, _, ln_end = buf.readline()[start_index:].split(" ")

        # Extract filepath from second line.
        _, filepath = buf.readline().split(" ")
        
        self.path     = filepath.strip()
        self.ln_end   = int(ln_end)
        self.ln_start = int(ln_start)

    def setQueryFile(self, path):
        self.query_path = path

    def setQueryTime(self, qt):
        self.query_time = qt
        
    def getQueryTime(self):
        if self.query_time > 0:
            return self.query_time
        
        else:
            raise Exception(
                    "Query time value is wrong. Maybe "
                    "it was not set? Query time: %d" % (self.query_time)
                    )
    
    def __str__(self):
        _repr = (
            "Code clone of query file '%s' "
            "found in file '%s' "
            "on lines %d to %d." % (
                                self.query_path, self.path, 
                                self.ln_start, self.ln_end
                                )
            )
            
        return _repr