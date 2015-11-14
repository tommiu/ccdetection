'''
Created on Nov 11, 2015

@author: Tommi Unruh
'''
from manual_search import ManualCCSearch
import pexpect
import subprocess
import os
import signal
import sys

class Neo4jHelper(object):
    """
    Handling of everything concerning neo4j.
    """
    
    SPAWN_SCRIPT = "/opt/phpjoern/spawn_neodb.sh"

    def __init__(self):
        '''
        Constructor
        '''
    
    @staticmethod
    def analyseData(code_and_path_and_process_number):
        """
        Create the PHP AST of the files in 'path', import them into the 
        neo4j graph database and start the neo4j console.
        Finally, run the analysing query against the graph database. 
        """
        code, path, process_number = code_and_path_and_process_number
        
        try:
            process = Neo4jHelper.prepareData(path, process_number)
            
            cc_tester = ManualCCSearch(7473 + process_number)
            cc_tester.runTimedQuery(cc_tester.runQuery, query=code)
    
            process.sendcontrol('c')
            process.close()
    
        except BindException as err:
            print err
            print "Trying 'pkill -f java -cp.+neo4j' and restart"
            process = pexpect.run("pkill -f \"java -cp /opt/neo4j-0%d\"" % (
                                                                    process_number
                                                                    ))
            Neo4jHelper.analyseData(code_and_path_and_process_number)
        
        print "process number:", process_number
        return process_number
    
    @staticmethod
    def prepareData(path, process_number=1):
        print "Analysing path: %s" % path
        process = pexpect.spawn(Neo4jHelper.SPAWN_SCRIPT, [path, str(process_number)], 360)
        
        expectation = process.expect([
                            "graph.db still exists", 
                            "Remote interface ready", 
                            "java.net.BindException",
                            ])
    
        if expectation == 2:
    #         print process.before
            raise BindException()
        
        return process
    
    def startConsole(self, path):
        """
        Import the php file/project AST from 'path' into the neo4j 
        database and start the neo4j console, using the 'SPAWN_SCRIPT' file.
        """
    #     print "Using path %s" % path
        process = subprocess.call(
                            [Neo4jHelper.SPAWN_SCRIPT, path, "1"],
    #                         shell=True,
                            preexec_fn=os.setsid
                            )
        
        def signalHandler(signalnum, handler):
            os.killpg(process.pid, signal.SIGINT)
            
        signal.signal(signal.SIGINT, signalHandler)
        signal.signal(signal.SIGTERM, signalHandler)
        
class BindException(BaseException):
    def __init__(self, msg=None):
        if msg:
            self.message = msg
            
        else:
            self.message = (
                    "java.net.BindException: Address already in use. "
                    "-> pkill neo4j."
                    )
            
    def __str__(self):
        return self.message