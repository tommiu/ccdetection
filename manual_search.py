'''
Created on Oct 27, 2015

@author: Tommi Unruh
'''

from joern.all import JoernSteps
import time

class ManualCCSearch(object):
    '''
    classdocs
    '''
    UNTRUSTED_DATA = """attacker_sources = [
                "_GET", "_POST", "_COOKIE",
                "_REQUEST", "_ENV", "HTTP_ENV_VARS"
                ]\n"""
    
    SQL_QUERY_FUNCS = """sql_query_funcs = [
                "mysql_query", "pg_query", "sqlite_query"
                ]\n"""
    
    # Gremlin operations
    ORDER_LN = ".order{it.a.lineno <=> it.b.lineno}" # Order by linenumber
    
    QUERIES_DIR = "/shared_data/workspace/ccdetection/gremlin_queries/"
    
    def __init__(self):
        '''
        Constructor
        '''
        self.j = JoernSteps()
        self.j.setGraphDbURL('http://localhost:7474/db/data/')
        self.j.addStepsDir("/opt/python-joern/joern/phpjoernsteps")
        self.j.connectToDatabase()
    
    def searchCCOne(self):
        """
        Search for the first vulnerable tutorial (SQL injection from stackoverflow):
        $user_alcohol_permitted_selection = $_POST['alcohol_check']; //Value sent using jquery .load()
        $user_social_club_name_input = $_POST['name']; //Value sent using jquery .load()

        $query="SELECT * FROM social_clubs 
        WHERE name = $user_social_club_name_input";    

        if ($user_alcohol_permitted_selection != "???")
        {
             $query.= "AND WHERE alcohol_permitted = $user_alcohol_permitted_selection";
        }
        """
        # construct gremlin query step by step:
        # 1. Find variable name X of "variable = $_POST[..]"
        # 2. Go to next statement list.
        # (3. Find variable name Y of "variable = $_POST[..]"
        # (4. Go to next statement list.
        # 5. Find variable name Z and string str1 of "variable = string"
        # 6. Check if str1 contains regexp "WHERE any_word=$Y".
        # (7. Go to next statement list.)
        # (8. Check for if-statement with variable $X.)
        # 9. Check if variable $Z is extended using string with regexp
        # "and where any_word=$X"
        # (10. Check for mysql_query($Z))
        
        # all nodes
#         query  = "g.V(NODE_TYPE, TYPE_STMT_LIST).out"
#         
#         # AST_ASSIGN nodes' right side
#         query += ".rval"

        query = "g.V"

        return query
    
    def sqlNewIndirect(self):
        query = self.UNTRUSTED_DATA + self.SQL_QUERY_FUNCS
        
        query += open(self.QUERIES_DIR + "sql_new_indirect.query", 'r').read()
    
        return query
    
    def runQuery(self, query):
        return query
    
    def runTimedQuery(self, myFunction, query=None):
        start = time.time()
        res = None
        
        if query:
            res = self.j.runGremlinQuery(myFunction(query))
        else:
            res = self.j.runGremlinQuery(myFunction())
        elapsed = time.time() - start
        
#         print "Query done in %f seconds." % (elapsed)
        try:
            for node in res:
                print node
        
        except TypeError:
            # res is not iterable, because it is one node only.
            print res