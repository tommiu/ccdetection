'''
Created on Sep 28, 2015

@author: Tommi Unruh
'''


import sys
from args_parser import ModeArgsParser
import os
import itertools

from LazyMP import LazyMP
from LazyMP import ProcessIdGenerator
from neo4j_helper import Neo4jHelper
from configurator import Configurator

ARGS_HELP    = "help"
ARGS_SEARCH  = "search"
ARGS_CONFIG  = "config"
ARGS_CONSOLE = "console"

CONFIG_PATH  = "config"

def main(argv):
    # Setup command line arguments.
    parser = ModeArgsParser()
    setupArgs(parser)
    
    try:
        flow = parser.parseArgs(argv[1], argv[2:])
        
    except:
        parser.printHelp(argv[0])
        sys.exit()

    # Make config point to the absolute path.
    full_path = os.path.abspath(argv[0])
    last_slash_index = full_path.rfind("/")
    base_dir = full_path[0:last_slash_index]
    
    global CONFIG_PATH
    CONFIG_PATH = base_dir + "/" + CONFIG_PATH

    if flow[parser.KEY_MODE] != ARGS_CONFIG:
        # Load config.
        Configurator.load(CONFIG_PATH)

    if flow[parser.KEY_MODE] == ARGS_HELP:
        parser.printHelp(argv[0])
        sys.exit()
    
    elif flow[parser.KEY_MODE] == ARGS_CONSOLE:
        Neo4jHelper().startConsole(os.path.abspath(flow["in"]))
    
    elif flow[parser.KEY_MODE] == ARGS_SEARCH:
        startSearchMode(flow)
        
    elif flow[parser.KEY_MODE] == ARGS_CONFIG:
        Configurator().setupConfig(
                                CONFIG_PATH, base_dir, getArg(flow, "p", "path")
                                )

    else:
        parser.printHelp(argv[0])
        sys.exit()

def startSearchMode(flow):
    flow["in"] = os.path.abspath(flow["in"])
    code = ""
    level = 0
    multithreads = 0
    neo4j_helper = Neo4jHelper()
    
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
        
    except ArgException:
        # Parameter "-l/--level" was not specified.
        pass
    
    if level == 0:
        # Analyse specified file/files in specified directory.
        neo4j_helper.analyseData((
                code, flow["in"], 1
                ))
    
    else:
        # Analyse folders 'level' levels under specified path.
        try:
            # Get the root directory of every project in a generator.
            path_generator = getRootDirectories(flow["in"], level)
            
        except Exception as err:
            print "An exception occured: %s" % err
            sys.exit()

    projects_analysed = 0
    
    if multithreads > 1:
        # Multithreading was specified.
        
        process_number_generator = ProcessIdGenerator()
        
        # Start a lazy pool of processes.
        pool = LazyMP().poolImapUnordered(
                analyseDataHelper, itertools.izip(
                        itertools.repeat(code), path_generator, 
                        process_number_generator.getGenerator([1,2,3,4]),
                        ),
                multithreads,
                process_number_generator
                )

        # And let them work.
        try:
            while True:
                # Let multiprocessing pool process all arguments.
                pool.next()
                projects_analysed += 1
                
        except Exception as err:
            # Done
            print err
            pass

    else:    
        # No multithreading.
        for path in path_generator:
            neo4j_helper.analyseData((
                    code, path, 1
                    ))
            projects_analysed += 1
    
    if projects_analysed == 0:
        print "No project analysed for path: '%s'" %(
                            flow["in"]
                            )

def analyseDataHelper(args):
    return Neo4jHelper.analyseData(args)

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
                "Setup the config file using the specified path in '-p/--path'."
                " The config file contains all the necessary paths for "
                "ccdetection to work correctly."
                )
    parser.addArgumentsCombination(
                                ARGS_CONFIG,
                                [["p=", "path"]],
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