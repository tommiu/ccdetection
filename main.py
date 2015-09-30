'''
Created on Sep 28, 2015

@author: Tommi Unruh
'''

import sys
from joern.all import JoernSteps

def main(args):
    j = JoernSteps()
    j.setGraphDbURL('http://localhost:7474/db/data/')
    j.addStepsDir("/opt/python-joern/joern/phpjoernsteps")
    j.connectToDatabase()
    
    res = j.runGremlinQuery('g.V')
    print "query done"
    
    for r in res:
        print r

if __name__ == '__main__':
    main(sys.argv[1:])
