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
        query = self.UNTRUSTED_DATA + self.SQL_QUERY_FUNCS + """
                
        def warning( id, type, filename, lineno) {
          "findsqlinjnew_indirect: In file " + filename + ": line " + lineno + " potentially dangerous (node id " + id + ", type " + type + ")"
        }
        
        def unexpected( id, type, filename, lineno) {
          "findsqlinjnew_indirect: Unexpected first argument to SQL query call in " + filename + ", line " + lineno + " (node id " + id + ", type " + type + ")"
        }
        
                
        g.V()
        
        // find all call expressions where the called function is called "mysql_query" / "pg_query" / "sqlite_query"
        .filter{ sql_query_funcs.contains(it.code) && isCallExpression(it.nameToCall().next()) }.callexpressions()
        
        // traverse to arguments; note that we do not know whether to traverse
        // to the first or second argument, so just collect them all (1)
        .callToArguments()
        
        // match variables (argument could be a variable itself, or contain
        // variables within a string concatenation or an encapsulated list)
        .match{ it.type == TYPE_VAR }
        
        // label here for looping
        .as('x')
        
        // save the variable node
        .sideEffect{ var = it }
        
        // traverse to enclosing function or file statements node
        .fileOrFunctionStmts()
        
        // match assignments whose left side is the saved variable name...
        .match{ isAssignment(it) && it.lval().varToName().next() == var.varToName().next() }
        
        // ...find the variables that occur on the right-hand side...
        .rval().match{ it.type == TYPE_VAR }
        
        // loop until nothing new is emitted, and emit all objects in each iteration
        .loop('x'){ it.object != null }{ true }
        
        // filter only the nodes contained in the attacker sources
        .filter{ attacker_sources.contains(it.varToName().next()) }
        
        // finally, when we get here, go back to the matched variable and emit a warning
        .back('x')
        .transform{ warning(it.id, it.type, it.toFile().fileToPath().next(), it.lineno) }
        """
    
        return query
    
    def runTimedQuery(self, myFunction):
        start = time.time()
        res = self.j.runGremlinQuery(myFunction())
        elapsed = time.time() - start
        
        print "Query done in %f seconds." % (elapsed)
        for node in res:
            print node