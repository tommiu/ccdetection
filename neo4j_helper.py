'''
Created on Nov 11, 2015

@author: Tommi Unruh
'''
from manual_search import ManualCCSearch
import pexpect
import subprocess
import os
import signal
from configurator import Configurator
import sys

class Neo4jHelper(object):
    """
    Handling of everything concerning neo4j.
    """

    HEAP_SIZE = [100, "G"] # G = Gigabyte, M = Megabyte

    def __init__(self):
        '''
        Constructor
        '''
    
    @staticmethod
    def setHeapsize(size, unit):
        # Allowed units are "G" (gigabyte) or "M" (megabyte).
        if unit == "G" or unit == "M" and isinstance(size, int):
            Neo4jHelper.HEAP_SIZE[0:2] = size, unit
            
        else:
            raise Exception("Trying to set faulty heap size: %s%s." % (
                                                                str(size), unit
                                                                ))
    
    @staticmethod
    def setStatisticsObj(obj):
        Neo4jHelper.stats = obj
    
    @staticmethod
    def analyseData(code_and_path_and_process_number):
        """
        Create the PHP AST of the files in 'path', import them into the 
        neo4j graph database and start the neo4j console.
        Finally, run the analysing query against the graph database. 
        """
        query_objects, path, process_number = code_and_path_and_process_number
        port = 7473 + process_number
        
        try:
            process = Neo4jHelper.prepareData(path, process_number)
            cc_tester = ManualCCSearch(port)
            
            first_query = True
            clones = []
            queries = []
            
            for query_file_obj in query_objects:
                result, elapsed_time = cc_tester.runTimedQuery(
                                        cc_tester.runQuery,
                                        query=query_file_obj.getCode()
                                        )
                if hasattr(Neo4jHelper, "stats"):
                    # Statistics are enabled, so add results to the statistics.
                    if result:
                        # Code clones found.
                        for clone in result:
                            clone.setQueryFile(query_file_obj.getFilename())
                            code_clone = {
                                        "clone": clone,
                                        "first": first_query
                                        }
                            clones.append(code_clone)
                    
                    else:
                        # No code clone found.
                        query = {
                            "query_time": elapsed_time,
                            "first": first_query
                            }
                        queries.append(query)
                        
                    first_query = False

            if hasattr(Neo4jHelper, "stats"):
                try:
                    Neo4jHelper.stats.saveData(queries, clones)
                except:
                    pass
            
            # Kill neo4j database server.
            process.sendcontrol('c')
            process.close()
    
        except BindException:
            print (
                "Port %d is taken. Trying to kill a neo4j graph database "
                "listening on that port and start an updated one." % port
                )
            
            Neo4jHelper.killProcess(process_number)
            return Neo4jHelper.analyseData(code_and_path_and_process_number)
        
        except PathException:
            exception = "Could not create directory in ccdetection/graphs/."
            print exception
            return Neo4jHelper.analyseData(code_and_path_and_process_number)
        
        except HeapException:
            print "There is insufficient memory for allocating the heap size."
            print "Created a hs_err_pid* file with more information."
            
            if Neo4jHelper.HEAP_SIZE[0] > 1 and Neo4jHelper.HEAP_SIZE[1] == "G":
                new_size = Neo4jHelper.HEAP_SIZE[0] - 1
                unit = "G" 
            
            elif (
                    Neo4jHelper.HEAP_SIZE[0] == 1 and 
                    Neo4jHelper.HEAP_SIZE[1] == "G"
            ):
                new_size = Neo4jHelper.HEAP_SIZE[0] = 512
                unit = "M"
                
            if Neo4jHelper.HEAP_SIZE[1] == "M":
                new_size = Neo4jHelper.HEAP_SIZE[0] / 2
                unit = "M"
            
            print "Trying again with %d%s memory for the heap." % (
                                                                new_size, unit
                                                                )
            print ( 
                "Change the heap_size parameter in the config file for a "
                "permanent solution."
                )
            
            Neo4jHelper.setHeapsize(new_size, unit)
            return Neo4jHelper.analyseData(code_and_path_and_process_number)
        
        except Exception as err:
            print err
            raise Exception("Critical error, exiting.")
        
        return process_number
    
    @staticmethod
    def prepareData(path, process_number=1):
        print "Analysing path: %s" % path

        process = pexpect.spawn(
                            Configurator.getPath(Configurator.KEY_SPAWN_SCRIPT),
                            [
                    Configurator.getPath(Configurator.KEY_BASE_DIR) + "/config", 
                    path, str(process_number), 
                    "%d%s" % (Neo4jHelper.HEAP_SIZE[0], 
                              Neo4jHelper.HEAP_SIZE[1])
                    ],
                            None
                            )
        
        if Configurator.isDebuggingEnabled():
            process.logfile = sys.stdout
        
        expectation = process.expect([
#                         "graph.db still exists", 
                        "Remote interface ready", 
                        "java.net.BindException",
                        "java.io.IOException: Unable to create directory path",
                        pexpect.EOF,
                        "ERROR: No write access to data/ directory",
                        (
                    "There is insufficient memory for the Java Runtime "
                    "Environment to continue."
                    )
                        ])
        
        if expectation == 1:
            # BindException (port already taken?)
            raise BindException()
        
        elif expectation == 2:
            # Unable to create directory path
            raise PathException()
       
        elif expectation == 3:
            # EOF
            # print process.before
            raise BindException()
        
        elif expectation == 4:
            raise Exception(
                    "ERROR: No write access to neo4j data directory. "
                    "Check for sufficient write permissions in all neo4j "
                    "instances' data directory."
                    )
            
        elif expectation == 5:
            # Not enough space to allocate the specified amount of heap space.
            raise HeapException()

        return process
    
    def startConsole(self, path, port=1):
        """
        Import the php file/project AST from 'path' into the neo4j 
        database and start the neo4j console, using the 'SPAWN_SCRIPT' file.
        """
        process = subprocess.call(
                            [
                    Configurator.getPath(Configurator.KEY_SPAWN_SCRIPT),
                    Configurator.getPath(Configurator.KEY_BASE_DIR) + "/config", 
                    path, str(port), 
                    "%d%s" % (Neo4jHelper.HEAP_SIZE[0], 
                              Neo4jHelper.HEAP_SIZE[1])
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

class PathException(Exception):
    pass

class HeapException(Exception):
    pass
