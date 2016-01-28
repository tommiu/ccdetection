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
from query_file import QueryFile
from results.shared_data import SharedData
import multiprocessing
from multiprocessing import Value

ARGS_HELP    = "help"
ARGS_SEARCH  = "search"
ARGS_CONFIG  = "config"
ARGS_CONSOLE = "console"
ARGS_PRINT_STATS = "print_stats"
ARGS_PRINT_RESULTS = "print_results"
ARGS_CONTINUOUS_SEARCH  = "continuous_search"
ARGS_COMBINE_STATISTICS = "combine_stats"

CONFIG_PATH = "config"
DEFAULT_STATS_PATH  = "stats"

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

    # Set debugging.
    try:
        getArg(flow, "d", "debug")
        Configurator.setDebugging(True)
    
    except ArgException as err:
#         # Debugging was not specified.
        pass
        
    if flow[parser.KEY_MODE] != ARGS_CONFIG:
        # Load config.
        Configurator.load(CONFIG_PATH)

    if flow[parser.KEY_MODE] == ARGS_HELP:
        parser.printHelp(argv[0])
        sys.exit()
        
    elif flow[parser.KEY_MODE] == ARGS_COMBINE_STATISTICS:
        combineStatsFiles(flow)
    
    elif flow[parser.KEY_MODE] == ARGS_CONSOLE:
        id = 1
        try:
            id = getArg(flow, "id")
        
        except:
            pass
        
        Neo4jHelper().startConsole(os.path.abspath(flow["in"]), str(id))
    
    elif flow[parser.KEY_MODE] == ARGS_SEARCH:
        startSearchMode(flow)
        
    elif flow[parser.KEY_MODE] == ARGS_CONTINUOUS_SEARCH:
        startSearchMode(flow, continuous=True)
        
    elif flow[parser.KEY_MODE] == ARGS_CONFIG:
        Configurator().setupConfig(
                                CONFIG_PATH, base_dir, getArg(flow, "p", "path")
                                )
    
    elif flow[parser.KEY_MODE] == ARGS_PRINT_STATS:
        printStats(flow)
        
    elif flow[parser.KEY_MODE] == ARGS_PRINT_RESULTS:
        printResults(flow)

    else:
        parser.printHelp(argv[0])
        sys.exit()
        
def printStats(flow):
    try:
        stats_path = getArg(flow, 's', 'statsfile')
    except:
        stats_path = DEFAULT_STATS_PATH
    
    if os.path.isfile(stats_path):
        print "Statistics file: '%s'" % (stats_path)
        print SharedData(stats_path, multiprocessing.Lock())
    else:
        print "Given path is not a valid file: '%s'" % (stats_path)

def printResults(flow):
    try:
        stats_path = getArg(flow, 's', 'statsfile')
    except:
        stats_path = DEFAULT_STATS_PATH
    
    if os.path.isfile(stats_path):
        clones = SharedData(stats_path, multiprocessing.Lock()).getClones()
        print "Found %d code clones saved in file '%s':" % (
                                                        len(clones), stats_path
                                                        )
        for i, clone in enumerate(clones):
            print str(i) + ".", clone
            
    else:
        print "Given path is not a valid file: '%s'" % (stats_path)
        
        
def combineStatsFiles(flow):
    _files = getArg(flow, "s", "stats")
    _out   = getArg(flow, "out")
    
    _files = _files.split(",")
    
    try:
        # Remove empty elements.
        _files.remove("")
        
    except ValueError as err:
        # No element was removed.
        pass
    
    # Remove unnecessary whitespace characters.
    _files = [_file.strip() for _file in _files]
    
    
    if len(_files) > 1:
        for _file in _files:
            if not os.path.isfile(_file):
                raise Exception("'%s' is not a file." % (_file))
            
        lock = multiprocessing.Lock()
        first_data = SharedData(_files[0], lock)
        
        for _file in _files[1:]:
            data = SharedData(_file, lock)
            first_data.combineWith(data)
            
        first_data.saveToFile(_out)
        
        print "Stats files combined into '%s'" % (_out)
        
    else:
        print "Specify more than one statistics file. Separate them with commas."
        print "I.e. -s \"\""
        
def startSearchMode(flow, continuous=False):
    flow["in"] = os.path.abspath(flow["in"])
    if not os.path.exists(flow["in"]):
        print "Given path (-in) does not exist."
        sys.exit()
    
    level = 0
    multithreads = 0
    neo4j_helper = Neo4jHelper()
    
    if continuous:
        # Continuous mode was specified, so read the config file
        try:
            stats_path = getArg(flow, "s", "statsfile")
        except:
            stats_path = DEFAULT_STATS_PATH

        lock = multiprocessing.Lock()
        shared_data = SharedData(stats_path, lock, in_path=flow["in"])
        in_path = shared_data.getInPath()
        
        if in_path != flow["in"]:
                    print (
                        "The given path with \"-in\" is not the path, "
                        "which was used before."
                        )
                    _ = raw_input("Ctrl-C or Ctrl-D to abort. "
                                           "Press any key to continue")
        
        shared_data.setInPath(flow["in"])
        
        Neo4jHelper.setStatisticsObj(shared_data)

    try:
        multithreads = int(getArg(flow, "m", "multithreading"))
    except:
        pass

    code_path = getArg(flow, "q", "queries")
    code = []

    # Read given query.
    if os.path.isfile(code_path):
        with open(code_path, "r") as fh:
            code.append(
                    QueryFile(code_path, fh.read())
                    )
    
    elif os.path.isdir(code_path):
        # Given path is a directory - get all files recursively inside the
        # directory.
        for path, _, files in os.walk(code_path):
            for name in files:
                file_path = os.path.join(path, name)
                with open(file_path, "r") as fh:
                    code.append(
                            QueryFile(file_path, fh.read())
                            )
        
        if not code:
            # Did not find any file recursively inside 'code_path'.
            print "Query-path (-q/--queries) does not contain any files."
            sys.exit()
                    
    else:
        # Path does not exist
        print "Query-Path (-q/--queries) does not exist."
        sys.exit()
    
    
    try:
        level = int(getArg(flow, "l", "level"))
        
    except ArgException:
        # Parameter "-l/--level" was not specified.
        pass
    
    if level == 0:
        # Analyse specified file/files in specified directory with given
        # gremlin query/queries.
        Neo4jHelper.analyseData((
                code, flow["in"], 1
                ))
    
    else:
        # Analyse folders 'level' levels under specified path.
        try:
            # Get the root directory of every project in a generator.
            path_generator = getRootDirectories(flow["in"], level)
            
            if continuous:
                # Check if given in-path is the same as the one in the
                # given stats file.
                
                if in_path == flow["in"]:
                    # Skip generator elements if they were already
                    # analysed before.
                    projects_analysed_count = shared_data.getProjectsCount()
                    skipGeneratorElements(path_generator, projects_analysed_count)

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

def skipGeneratorElements(_gen, count):
    try:
        for _ in xrange(count):
            print "Skipping", _gen.next()
    except StopIteration:
        raise Exception("Could not skip given paths as expected, stopping.")
        

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
                for path in traversePath(
                        destination_list, _path, 
                        current_level + 1, target_level
                        ):
                    yield path

def setupArgs(parser):
    """
    Setup command line arguments combinations.
    """
    # Help: help
    explanation = "Print this help."
    parser.addArgumentsCombination(ARGS_HELP, explanation=explanation)
    
    # Search code clones: search -q file -in dir/file
    explanation = (
                "Search clones of the code snippet in file specified with "
                "-q/--queries in directory or file specified with -in. In the "
                "case of a dictionary full of project dictionaries, "
                "you can analyse each project on its own by "
                "specifying -l/--level 1. Level==1 means, that "
                "the top level directory of each project is one directory "
                "deeper than the path specified. "
                "-d/--debug enables debugging output."
                )
    parser.addArgumentsCombination(
                                ARGS_SEARCH,
                                [
                            ["q=", "queries"],
                            ["in=", None]
                            ],
                                [
                            ["l=", "level"],
                            ["m=", "multithreading"],
                            ["d", "debug"]
                            ],
                                explanation=explanation
                                )
    
    # Search code clones: continuous_search -q file -in paths_file (-s file)
    explanation = (
                "Extension of the search mode: Additionally to searching "
                "code clones, a file is used to record statistical data "
                "across multiple executions of the continuous_search. "
                "The default path for the stats file is './stats', but it "
                "can be modified using the -s/--statsfile parameter."
                )
    parser.addArgumentsCombination(
                                ARGS_CONTINUOUS_SEARCH,
                                [
                            ["q=", "queries"],
                            ["in=", None]
                            ],
                                [
                            ["l=", "level"],
                            ["m=", "multithreading"],
                            ["d", "debug"],
                            ["s=", "statsfile"]
                            ],
                                explanation=explanation
                                )
    
    # Print statistical data: print_stats (-s file)
    explanation = (
                "Print out the statistical data, that has been collected "
                "by using the continuous_search mode before."
                )
    parser.addArgumentsCombination(
                                ARGS_PRINT_STATS,
                                [],
                                [["s=", "statsfile"]],
                                explanation=explanation
                                )
    
    
    # Print results (found code clones): print_results (-s file)
    explanation = (
                "Print out the results (=found code clones) from previous "
                "'continuous_search'-mode runs."
                )
    parser.addArgumentsCombination(
                                ARGS_PRINT_RESULTS,
                                [],
                                [["s=", "statsfile"]],
                                explanation=explanation
                                )
    
    # Configurate paths for ccdetection: config -p/--path dir/file
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
                "Import the php file/project AST into the Neo4j database and "
                "start the Neo4j console. "
                "Use \"-id integer\" to use another Neo4j database instance."
                )
    parser.addArgumentsCombination(
                                ARGS_CONSOLE,
                                [["in=", None]],
                                [["id=", None]],
                                explanation=explanation
                                )
    
    # Combine stats files: console -s/--stats "file1, file2, ..." -out file
    explanation = (
                "Combine multiple statistics files specified with -s/--stats"
                ", separated by commas, into one and save it "
                "to the path specified with -out."
                )
    parser.addArgumentsCombination(
                                ARGS_COMBINE_STATISTICS,
                                [
                            ["s=", "stats"], 
                            ["out=", None]
                            ],
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