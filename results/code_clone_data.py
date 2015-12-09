'''
Created on Dec 8, 2015

@author: tommi
'''
import StringIO

class CodeCloneData(object):
    """
    Class to save and analyse the output of the ccdetection search.
    """


    def __init__(self):
        '''
        Constructor
        '''
        self.path = ""
        self.ln_start = -1
        self.ln_end = -1
        self.query_time = -1
        
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