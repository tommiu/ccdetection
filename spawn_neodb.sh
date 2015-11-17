#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] ; then
    echo "You need to specify three program arguments:"
    echo "1. Path to the ccdetection config file. 2. Path to the PHP project to parse. 3. The graph database id (1-4)."
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

PATH_NEO4J=$(readVal $1 "neo4j")
PATH_PHPJOERN=$(readVal $1 "phpjoern")
PATH_GRAPHDBS=$(readVal $1 "graphdbs")
PATH_BATCH_IMPORT=$(readVal $1 "batch_import")

# Delete old database
rm $PATH_GRAPHDBS/graph${2}.db/ -r

if [ -z "$JEXP_HOME" ]; then
    JEXP_HOME=`echo $PATH_BATCH_IMPORT`
fi

# Create PHP AST from path.
${PATH_PHPJOERN}/parser_$3 "$2"

# Create graph database from AST.
HEAP=6G; java -classpath "$JEXP_HOME/lib/*" -Xmx$HEAP -Xms$HEAP -Dfile.encoding=UTF-8 org.neo4j.batchimport.Importer ${PATH_PHPJOERN}/conf/batch.properties ${PATH_GRAPHDBS}/graph${3}.db ${PATH_PHPJOERN}/nodes.csv${3} ${PATH_PHPJOERN}/rels.csv${3}

# Start neo4j graph database server.
${PATH_NEO4J}/neo4j-0${3}/bin/neo4j console
