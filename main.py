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
        analyseData(flow["in"])

    else:
        parser.printHelp(argv[0])
        sys.exit()
    
def analyseData(path):
    process = prepareData(path)
    
    cc_tester = ManualCCSearch()
#     test1 = cc_tester.runTimedQuery(cc_tester.searchCCOne)
    cc_tester.runTimedQuery(cc_tester.sqlNewIndirect)
    
    process.sendcontrol('c')
    process.close()    

def prepareData(path):
    print "Analysing path: %s" % os.path.abspath(path)
    process = pexpect.spawn("/bin/bash", ["/opt/phpjoern/spawn_neodb.sh", path], 15)
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
                "case of dictionaries, you can search files recursively, by "
                "specifying -r/--recursive."
                )
    parser.addArgumentsCombination(
                                ARGS_SEARCH,
                                [
                            ["c=", "code"],
                            ["in=", None]
                            ],
                                [["r", "recursive"]],
                                explanation=explanation
                                )

if __name__ == '__main__':
    main(sys.argv)
