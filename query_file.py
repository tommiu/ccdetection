'''
Created on Dec 7, 2015

@author: Tommi Unruh
'''

class QueryFile(object):
    """
    Struct-class.
    """


    def __init__(self, filename, code):
        '''
        Constructor
        '''
        self.filename = filename
        self.code = code
        
    def getCode(self):
        return self.code
    
    def getFilename(self):
        return self.filename
    
        