#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "You need to specify four program arguments:"
    echo "1. Path to the ccdetection config file. 2. Path to the PHP project to parse. 3. The graph database id (1-4). 4. Output directory for the php parser."
    exit
fi

if [ ! -f $1 ] ; then 
    echo -e "Config file specified with first program argument does not exist.\n Given path was: $1"
    exit
fi

function readVal {
    while read p; do
        key=$(echo $p | cut -f1 -d=)
        path=$(echo $p | cut -f2 -d=)

        if [ $key = $2 ] ; then
            echo "$path"
        fi
    done < $1
}

CONFIG_FILE=$1
PHP_PROJECT_PATH=$2
GRAPH_ID=$3
PARSE_OUTPUT_DIR=$4

PATH_NEO4J=$(readVal $CONFIG_FILE "neo4j")
PATH_PHPJOERN=$(readVal $CONFIG_FILE "phpjoern")
PATH_PHPPARSER=$(readVal $CONFIG_FILE "php_parser")
PATH_GRAPHDBS=$(readVal $CONFIG_FILE "graphdbs")
PATH_BATCH_IMPORT=$(readVal $CONFIG_FILE "batch_import")
PATH_PHPPARSE_RESULTS=$(readVal $CONFIG_FILE "php_parser_results")

# Delete old database
rm $PATH_GRAPHDBS/graph${GRAPH_ID}.db/ -r

if [ -z "$JEXP_HOME" ]; then
    JEXP_HOME=`echo $PATH_BATCH_IMPORT`
fi

# Create PHP AST from path.
# Parser arguments:
# 1. PHP files/directory to parse.
# 2. Output directory.
# 3. Appendix to filename (to distinguish output from multiple php parses).
# 4. Path to PHPJOERN
echo "${PATH_PHPPARSER}/parser $PHP_PROJECT_PATH $PARSE_OUTPUT_DIR $GRAPH_ID $PATH_PHPJOERN"
echo "$JEXP_HOME ${PATH_GRAPHDBS} ${PATH_PHPPARSE_RESULTS}"
${PATH_PHPPARSER}/parser $PHP_PROJECT_PATH $PARSE_OUTPUT_DIR $GRAPH_ID $PATH_PHPJOERN

# Create graph database from AST.
HEAP=6G; java -classpath "$JEXP_HOME/lib/*" -Xmx$HEAP -Xms$HEAP -Dfile.encoding=UTF-8 org.neo4j.batchimport.Importer ${PATH_PHPJOERN}/conf/batch.properties ${PATH_GRAPHDBS}/graph${GRAPH_ID}.db ${PATH_PHPPARSE_RESULTS}/nodes.csv${GRAPH_ID} ${PATH_PHPPARSE_RESULTS}/rels.csv${GRAPH_ID}

# Start neo4j graph database server.
${PATH_NEO4J}/neo4j-0${GRAPH_ID}/bin/neo4j console
