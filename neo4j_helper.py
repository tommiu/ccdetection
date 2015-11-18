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
from configurator import Configurator

class Neo4jHelper(object):
    """
    Handling of everything concerning neo4j.
    """

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
        
        port = 7473 + process_number
        try:
            process = Neo4jHelper.prepareData(path, process_number)
            cc_tester = ManualCCSearch(port)
            cc_tester.runTimedQuery(cc_tester.runQuery, query=code)

            # Kill neo4j database server.
            process.sendcontrol('c')
            process.close()
    
        except BindException as err:
            print (
                "Port %d is taken. Trying to kill a neo4j graph database "
                "listening on that port and start an updated one." % port
                )
            
            Neo4jHelper.killProcess(process_number)
            Neo4jHelper.analyseData(code_and_path_and_process_number)
        
        return process_number
    
    @staticmethod
    def prepareData(path, process_number=1):
        print "Analysing path: %s" % path
        process = pexpect.spawn(
                            Configurator.getPath(Configurator.KEY_SPAWN_SCRIPT),
                            [
                    Configurator.getPath(Configurator.KEY_BASE_DIR) + "/config", 
                    path, str(process_number),
                    Configurator.getPath(Configurator.KEY_PHP_PARSE_RESULTS) 
                    ],
                            360
                            )
        
        expectation = process.expect([
                            "graph.db still exists", 
                            "Remote interface ready", 
                            "java.net.BindException",
                            ])
    
        if expectation == 2:
            raise BindException()
        
        return process
    
    def startConsole(self, path):
        """
        Import the php file/project AST from 'path' into the neo4j 
        database and start the neo4j console, using the 'SPAWN_SCRIPT' file.
        """
    #     print "Using path %s" % path
        process = subprocess.call(
                            [
                    Configurator.getPath(Configurator.KEY_SPAWN_SCRIPT),
                    Configurator.getPath(Configurator.KEY_BASE_DIR) + "/config", 
                    path, "1",
                    Configurator.getPath(Configurator.KEY_PHP_PARSE_RESULTS)
                    ],
                            preexec_fn=os.setsid
                            )
        
        def signalHandler(signalnum, handler):
            os.killpg(process.pid, signal.SIGINT)
            
        signal.signal(signal.SIGINT, signalHandler)
        signal.signal(signal.SIGTERM, signalHandler)
        
    @staticmethod
    def killProcess(process_number):
        kill_regex = "\"java -cp .*neo4j-0%d.*\"" % process_number
        process = pexpect.spawn("pkill -f %s" % (kill_regex))
        
        # Wait until child finishes.
        process.expect(pexpect.EOF)
    
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