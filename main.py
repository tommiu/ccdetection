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


ARGS_HELP = "help"
ARGS_SEARCH = "search"

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
        
    elif flow[parser.KEY_MODE] == ARGS_SEARCH:
        flow["in"] = os.path.abspath(flow["in"])
        if "l" in flow or "level" in flow:
            level = 0
            if "l" in flow:
                level = int(flow["l"])
            else:
                level = int(flow["level"])
                
            try:
                paths = getRootDirectories(flow["in"], level)
                
            except Exception as err:
                print "An exception occured: %s" % err
                sys.exit()
                
            if paths:
                for path in paths:
                    analyseData(path)
                
            else:
                print "There is no top-level directory %d levels below '%s'" %(
                                    level, flow["in"]
                                    )
        else:
            analyseData(flow["in"])

    else:
        parser.printHelp(argv[0])
        sys.exit()
    
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
    traversePath(root_directories, path, 1, level)
    
    return root_directories

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
                destination_list.append(_path)
                
            else:
                # Traverse directory deeper.
                traversePath(destination_list, _path, current_level + 1, target_level)

def analyseData(path):
    """
    Create the PHP AST of the files in 'path', import them into the 
    neo4j graph database and start the neo4j console.
    Finally, run the analysing query against the graph database. 
    """
    process = prepareData(path)
    
    cc_tester = ManualCCSearch()
    cc_tester.runTimedQuery(cc_tester.sqlNewIndirect)
    
    process.sendcontrol('c')
    process.close()    

def prepareData(path):
    print "Analysing path: %s" % path
#     process = pexpect.spawn("/bin/bash", ["/opt/phpjoern/spawn_neodb.sh", path], 15)
    process = pexpect.spawn("/opt/phpjoern/spawn_neodb.sh", [path,], 15)
    process.expect(["graph.db still exists", "Remote interface ready"])
    print process.before
    
    return process
    
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
                                [["l=", "level"]],
                                explanation=explanation
                                )

if __name__ == '__main__':
    main(sys.argv)
