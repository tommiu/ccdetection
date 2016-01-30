'''
Created on Nov 14, 2015

@author: Tommi Unruh
'''
import os
import stat

class Configurator(object):
    """
    Writes and loads data from a config file.
    """

    KEY_NEO4J = "neo4j"
    KEY_GRAPHDBS  = "graphdbs"
    KEY_BASE_DIR  = "basedir"
    KEY_PHP_JOERN = "phpjoern"
    KEY_PHP_PARSER   = "php_parser"
    KEY_SPAWN_SCRIPT = "spawn_script"
    KEY_PYTHON_JOERN = "python_joern"
    KEY_BATCH_IMPORT = "batch_import"
    KEY_PHP_PARSE_RESULTS = "php_parser_results"
    
    PATH_NEO4j = "neo4j"
    PATH_GRAPHDBS  = "graphs"
    PATH_PHP_JOERN = "phpjoern"
    PATH_PHP_PARSER   = "AST_parser"
    PATH_SPAWN_SCRIPT = "spawn_neodb.sh"
    PATH_PYTHON_JOERN = "python-joern"
    PATH_BATCH_IMPORT = "batch-import"
    PATH_PHP_PARSE_RESULTS = "parse_results"
    
    debugging = False
    
    def __init__(self):
        pass
    
    @staticmethod
    def readLine(_line):
        """
        Return (key, value) of a read line.
        None for empty lines and ValueError on format errors.
        """
        if _line.strip() == "":
            return None
        
        key, value = _line.split("=", 1)
    
        key   = key.strip()
        value = value.strip()
        
        return (key, value)
    
    @staticmethod
    def load(config_path):
        Configurator.readFullConfigFile(config_path)
    
    @staticmethod
    def readFullConfigFile(config_path):
        Configurator.config = {}
        
        with open(config_path, 'r') as fh:
            cnt = 0
            for _line in fh:
                cnt += 1
                # Parse line
                try:
                    res = Configurator.readLine(_line)
                    
                    if res:
                        key, value = res
                        Configurator.config[key] = value
                except:
                    # Format error
                    raise ConfigException(
                            "Format error in config file on line %d." % (cnt)
                            )

    def setupConfig(self, config_path, base_dir, path, start_port=7473):
        config_dict = {}
        
        if path[-1] == "/":
            path = path[:-1]
        
        config_dict[self.KEY_NEO4J] = path + "/" + self.PATH_NEO4j
        config_dict[self.KEY_BASE_DIR]  = base_dir
        config_dict[self.KEY_GRAPHDBS]  = base_dir + "/" + self.PATH_GRAPHDBS
        config_dict[self.KEY_PHP_JOERN] = path     + "/" + self.PATH_PHP_JOERN
        config_dict[self.KEY_PYTHON_JOERN] = path + "/" + self.PATH_PYTHON_JOERN
        config_dict[self.KEY_BATCH_IMPORT] = path + "/" + self.PATH_BATCH_IMPORT
        config_dict[self.KEY_SPAWN_SCRIPT] = base_dir + "/" + \
                                                self.PATH_SPAWN_SCRIPT 
        config_dict[self.KEY_PHP_PARSER] = base_dir + "/" + self.PATH_PHP_PARSER
        config_dict[self.KEY_PHP_PARSE_RESULTS] = (
                                    config_dict[self.KEY_PHP_PARSER] + "/" +
                                    self.PATH_PHP_PARSE_RESULTS
                                    )
        
        self.writeConfigFile(
                        config_path,
                        config_dict
                        )
        
        if not os.path.exists(config_dict[self.KEY_GRAPHDBS]):
            # Ignore the race condition here, it does not matter.
            # Create the directory for the several graph databases.
            os.makedirs(config_dict[self.KEY_GRAPHDBS])
            
        if not os.path.exists(config_dict[self.KEY_PHP_PARSE_RESULTS]):
            # Ignore the race condition here, it does not matter.
            # Create the directory for the PHP AST parsing results.
            os.makedirs(config_dict[self.KEY_PHP_PARSE_RESULTS])
        
        # Write the server config file for every neoj4 instance.
        # They differ in the ports (http and https) they use.
        neo_4j_path = config_dict[self.KEY_NEO4J] + \
                        "/neo4j-0%d/conf/neo4j-server.properties"
                        
        # Check number of neo4j instances
        
        neo4j_count = 0
        for path in os.listdir(config_dict[self.KEY_NEO4J]):
            if os.path.isdir(os.path.join(config_dict[self.KEY_NEO4J], path)):
                if path[0:6] == "neo4j-":
                    neo4j_count += 1
        
        for i in range(1, neo4j_count + 1):
            self.writeNeo4jConfig(
                        neo_4j_path % i, start_port + i, start_port + 100 + i
                        )
        
        # Make scripts executable
        filepath = config_dict[self.KEY_SPAWN_SCRIPT]
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IEXEC)
        
        filepath = config_dict[self.KEY_PHP_PARSER] + "/parser"
        st = os.stat(filepath)
        os.chmod(filepath, st.st_mode | stat.S_IEXEC)
    
    def writeConfigFile(self, filepath, _dict):
        config_format = "%s = %s"
        with open(filepath, 'w') as fh:
            for key in _dict:
                fh.write(config_format % (key, _dict[key]) + "\n")
    
    @staticmethod
    def isDebuggingEnabled():
        return Configurator.debugging
    
    @staticmethod
    def setDebugging(_bool):
        Configurator.debugging = _bool
    
    @staticmethod
    def getPath(_key):
        val = Configurator.config[_key]
        if val:
            return val
        else:
            raise ValueError("'%s' is not specified in the config file.")
        
    def writeNeo4jConfig(self, path, port, port_ssl):
        default_config = """################################################################
# Neo4j configuration
#
################################################################

#***************************************************************
# Server configuration
#***************************************************************

# location of the database directory 
org.neo4j.server.database.location=data/graph.db

# Let the webserver only listen on the specified IP. Default is localhost (only
# accept local connections). Uncomment to allow any connection. Please see the
# security section in the neo4j manual before modifying this.
#org.neo4j.server.webserver.address=0.0.0.0

#
# HTTP Connector
#

# http port (for all data, administrative, and UI access)
org.neo4j.server.webserver.port=%d

#
# HTTPS Connector
#

# Turn https-support on/off
org.neo4j.server.webserver.https.enabled=true

# https port (for all data, administrative, and UI access)
org.neo4j.server.webserver.https.port=%d

# Certificate location (auto generated if the file does not exist)
org.neo4j.server.webserver.https.cert.location=conf/ssl/snakeoil.cert

# Private key location (auto generated if the file does not exist)
org.neo4j.server.webserver.https.key.location=conf/ssl/snakeoil.key

# Internally generated keystore (don't try to put your own
# keystore there, it will get deleted when the server starts)
org.neo4j.server.webserver.https.keystore.location=data/keystore

#*****************************************************************
# Administration client configuration
#*****************************************************************

# location of the servers round-robin database directory. Possible values:
# - absolute path like /var/rrd
# - path relative to the server working directory like data/rrd
# - commented out, will default to the database data directory.
org.neo4j.server.webadmin.rrdb.location=data/rrd

# REST endpoint for the data API
# Note the / in the end is mandatory
org.neo4j.server.webadmin.data.uri=/db/data/

# REST endpoint of the administration API (used by Webadmin)
org.neo4j.server.webadmin.management.uri=/db/manage/

# Low-level graph engine tuning file
org.neo4j.server.db.tuning.properties=conf/neo4j.properties

# The console services to be enabled
org.neo4j.server.manage.console_engines=shell


# Comma separated list of JAX-RS packages containing JAX-RS resources, one
# package name for each mountpoint. The listed package names will be loaded
# under the mountpoints specified. Uncomment this line to mount the
# org.neo4j.examples.server.unmanaged.HelloWorldResource.java from
# neo4j-server-examples under /examples/unmanaged, resulting in a final URL of
# http://localhost:7474/examples/unmanaged/helloworld/{nodeId}
#org.neo4j.server.thirdparty_jaxrs_classes=org.neo4j.examples.server.unmanaged=/examples/unmanaged


#*****************************************************************
# HTTP logging configuration
#*****************************************************************

# HTTP logging is disabled. HTTP logging can be enabled by setting this
# property to 'true'.
org.neo4j.server.http.log.enabled=false

# Logging policy file that governs how HTTP log output is presented and
# archived. Note: changing the rollover and retention policy is sensible, but
# changing the output format is less so, since it is configured to use the
# ubiquitous common log format
org.neo4j.server.http.log.config=conf/neo4j-http-logging.xml"""

        with open(path, 'w') as fh:
            fh.write(default_config % (port, port_ssl))
                
class ConfigException(BaseException):
    def __init__(self, msg=None):
        if msg:
            self.message = msg
            
        else:
            self.message = (
                    "Format error in config file."
                    )
            
    def __str__(self):
        return self.message