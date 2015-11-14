'''
Created on Nov 14, 2015

@author: Tommi Unruh
'''

class Configurator(object):
    """
    Writes and loads data from a config file.
    """

    BASE_DIR      = "basedir"
    PATH_NEO4J    = "neo4j"
    SPAWN_SCRIPT  = "spawn_script"
    PATH_PHPJOERN = "phpjoern"

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
    
    def setupConfig(self, path):
        config_dict = {}
        
        self.writeConfigFile(config_dict)
    
    def writeConfigFile(self, _dict):
        config_format = "%s = %s"
        with open(self.filepath, 'w') as fh:
            for key in _dict:
                fh.write(config_format % (key, _dict[key]))
    
    @staticmethod
    def getPath(_key):
        val = Configurator.config[_key]
        
        if val:
            return val
        else:
            raise ValueError("'%s' is not specified in the config file.")
                
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