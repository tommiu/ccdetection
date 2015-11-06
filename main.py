'''
Created on Sep 28, 2015

@author: Tommi Unruh
'''

import sys
from joern.all import JoernSteps
from time import sleep
from manual_search import ManualCCSearch
from args_parser import ModeArgsParser
import pexpect
import os
import signal
import subprocess
import multiprocessing
import itertools


ARGS_HELP    = "help"
ARGS_SEARCH  = "search"
ARGS_CONSOLE = "console"

SPAWN_SCRIPT = "/opt/phpjoern/spawn_neodb.sh"

def main(argv):
    # Setup command line arguments.
    parser = ModeArgsParser()
    setupArgs(parser)
    
    try:
        flow = parser.parseArgs(argv[1], argv[2:])
        
    except:
        parser.printHelp(argv[0])
        sys.exit()

    if flow[parser.KEY_MODE] == ARGS_HELP:
        parser.printHelp(argv[0])
        sys.exit()
    
    elif flow[parser.KEY_MODE] == ARGS_CONSOLE:
        startConsoleMode(os.path.abspath(flow["in"]))
    
    elif flow[parser.KEY_MODE] == ARGS_SEARCH:
        flow["in"] = os.path.abspath(flow["in"])
        code = ""
        code_path = ""
        multithreads = 0
        process_number = 1
        
        try:
            multithreads = int(getArg(flow, "m", "multithreading"))
        except:
            pass
        
        code_path = getArg(flow, "c", "code")
        
        # Read given code.
        with open(code_path, "r") as fh:
            code = fh.read()
        
        try:
            level = int(getArg(flow, "l", "level"))
        
            try:
                path_generator = getRootDirectories(flow["in"], level)
                
            except Exception as err:
                print "An exception occured: %s" % err
                sys.exit()
                
#             if paths:
#                 print "Found %d projects. Going to analyse them now." % (
#                                                                     len(paths)
#                                                                     )
            projects_analysed = 0
            
            if multithreads > 1:
                process_number_generator = generateProcessNumber()
                p = multiprocessing.Pool(multithreads)
                p.map(analyseData, itertools.izip(itertools.repeat(code), path_generator, process_number_generator))

            else:    
                for path in path_generator:
                    projects_analysed += 1
                    analyseData(code, path)
            
            if projects_analysed == 0:
                print "There is no top-level directory %d %s below '%s'" %(
                                    level, 
                                    "level" if level == 1 else "levels",
                                    flow["in"]
                                    )
            
        except ArgException:
            # Parameter "-l/--level" was not specified.
            analyseData((code, flow["in"], 1))

    else:
        parser.printHelp(argv[0])
        sys.exit()

def generateProcessNumber():
    i = 1
    while True:
        yield i
        i += 1
        if i > 4:
            i = 1
   
def getRootDirectories(path, level):    
    """
    Get all paths of the root directories.
    'level' specifies where the root directories are relatively to 'path'.
    E.g. a value of level=1 specifies, that any directory inside of 'path'
    is a root directory of a project.
    A value of level=2 specifies, that any directory inside a directory inside
    'path' is a root directory etc. 
    """
    # Wrong arguments handling #1.
    if not os.path.isdir(path):
        raise Exception("Specified path '%s' is not a directory." % path)
    
    # Wrong arguments handling #2.
    if level < 1:
        raise Exception(
                "Program argument '-l/--level %s has no effect. "
                "Do not use it or specify a value bigger than 0." % str(level)
                )
    
    root_directories = []
#     traversePath(root_directories, path, 1, level)
    
#     return root_directories
    return traversePath(root_directories, path, 1, level)

def traversePath(destination_list, path, current_level, target_level):
    """
    Create a list of absolute paths to directories, which are on a specific
    level below a given path, recursively.
    """
    for _path in os.listdir(path):
        # Create absolute path
        _path = "%s/%s" % (path, _path)

        if os.path.isdir(_path):
            if current_level == target_level:
                # This path is a directory and on the desired level - append it.
                yield _path
#                 destination_list.append(_path)
                
            else:
                # Traverse directory deeper.
                traversePath(
                        destination_list, _path, 
                        current_level + 1, target_level
                        )

def analyseData(code_and_path_process_number):
# def analyseData(code, path, process_number=1):
    """
    Create the PHP AST of the files in 'path', import them into the 
    neo4j graph database and start the neo4j console.
    Finally, run the analysing query against the graph database. 
    """
    code, path, process_number = code_and_path_process_number
    print path, process_number
    
    try:
        process = prepareData(path, process_number)
        
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
#         analyseData(code, path)
        analyseData(code_and_path_process_number)

def prepareData(path, process_number=1):
    print "Analysing path: %s" % path
    process = pexpect.spawn(SPAWN_SCRIPT, [path, str(process_number)], 360)
    
    expectation = process.expect([
                        "graph.db still exists", 
                        "Remote interface ready", 
                        "java.net.BindException",
                        ])

    if expectation == 2:
#         print process.before
        raise BindException()
    
    return process

def startConsoleMode(path):
    """
    Import the php file/project AST from 'path' into the neo4j 
    database and start the neo4j console, using the 'SPAWN_SCRIPT' file.
    """
#     print "Using path %s" % path
    process = subprocess.call(
                        [SPAWN_SCRIPT, path],
#                         shell=True,
                        preexec_fn=os.setsid
                        )
    
    def signalHandler(signalnum, handler):
        os.killpg(process.pid, signal.SIGINT)
        
    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
            
def setupArgs(parser):
    """
    Setup command line arguments combinations.
    """
    # Help: help
    explanation = "Print this help."
    parser.addArgumentsCombination(ARGS_HELP, explanation=explanation)
    
    # Search code clones: search -c file -in dir/file (-r)
    explanation = (
                "Search clones of the code snippet in file specified with "
                "-c/--code in directory or file specified with -in. In the "
                "case of a dictionary full of project dictionaries, "
                "you can analyse each project on its own by "
                "specifying -l/--level 1. Level==1 means, that "
                "the top level directory of each project is one directory "
                "deeper than the path specified."
                )
    parser.addArgumentsCombination(
                                ARGS_SEARCH,
                                [
                            ["c=", "code"],
                            ["in=", None]
                            ],
                                [
                            ["l=", "level"],
                            ["m=", "multithreading"]
                            ],
                                explanation=explanation
                                )
    
    # Open neo4j console: console -in dir/file
    explanation = (
                "Import the php file/project AST into the neo4j database and "
                "start the neo4j console."
                )
    parser.addArgumentsCombination(
                                ARGS_CONSOLE,
                                [["in=", None]],
                                explanation=explanation
                                )

def getArg(_list, key1, key2=None):
    result = ""
    try:
        result = _list[key1]
    except:
        if key2:
            try:
                result = _list[key2]
            
            except:
                raise ArgException()
        
        else:
            raise ArgException()
        
    return result

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

class ArgException(BaseException):
    def __init__(self, msg=None):
        if msg:
            self.message = msg
            
        else:
            self.message = (
                    "Parameter was not specified."
                    )
            
    def __str__(self):
        return self.message
            
if __name__ == '__main__':
    main(sys.argv)