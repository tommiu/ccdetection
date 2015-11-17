#!/bin/bash

# This script can be used on debian based systems to install all tools necessary for the ccdetection to work.
# This includes phpjoern, python-joern, PHP7, the graph database neo4j version 2.1, its Gremlin-plugin, batch-import 2.1.
# Some tools need to be compiled on your system, so that autoconf and maven will be used. Furthermore, all dependencies for compilation need to be available on the system.
# If any compiling process exits with missing file errors, resolve its dependencies, comment out all successfully finished steps in this script and restart it to continue.

# DEPENDENCIES FOR THIS SCRIPT TO WORK:
# Java JDK (tested with OpenJDK 7)
# E.g. to install OpenJDK 7: sudo apt-get install openjdk-7-jdk

function informRestart {
	echo "Install failed at step $3. Restart using following command:"
	echo "./install.sh $1 $2 $3"
}

if [ -z "$1" ]; then
	echo "Please specify a path to install all utilities to as first program argument."
	exit
fi

if [ -z "$2" ]; then
	echo "Please specify the number of CPUs to use as second program argument."
	exit
fi

if [ -z "$3" ]; then
	SKIP=0
else
	SKIP=$3

fi

INSTALL_PATH=$1
NEO4J_BASEDIR=$1/neo4j
CPUS=$2

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if (("$SKIP" == "0")) ; then
sudo apt-get update
# Following tools will be used to install everything:
sudo apt-get install autoconf bison flex maven unzip libxml2-dev -y

fi

cd $INSTALL_PATH

if (("$SKIP" < "2")) ; then
# Get phpjoern and python-joern
if ! git clone ssh://git@service.cispa.uni-saarland.de:2222/phpjoern.git
	then
	informRestart $1 $2 1
	exit
fi
fi

if (("$SKIP" < "3")) ; then
if ! git clone ssh://git@service.cispa.uni-saarland.de:2222/python-joern.git
	then
	informRestart $1 $2 2
	exit
fi
fi

# Get PHPJoernSteps extension for python-joern.
cd python-joern
git checkout portPHPJoern

# Install custom gremlin steps for python-joern.
cp -r $THIS_SCRIPT_DIR/custom_gremlin_steps $INSTALL_PATH/python-joern/joern/phpjoernstepsi/.

if (("$SKIP" < "4")) ; then
# Download PHP7 - ~160 MB
if ! mkdir php7
	then
	informRestart $1 $2 3
	exit
fi
fi

if ! cd $INSTALL_PATH/php7
	then
	exit
fi

if (("$SKIP" < "5")) ; then
if ! git clone https://git.php.net/repository/php-src.git
	then
	informRestart $1 $2 4
	exit
fi
fi

cd php-src

if (("$SKIP" < "6")) ; then
cd ext
if ! git clone https://github.com/nikic/php-ast.git ast
	then
	informRestart $1 $2 5
	exit
fi

cd ..
fi

# Build PHP7 - Errors are common in this step, when dependencies are missing to build PHP7.
# Fix the error message by installing the missing dependency and restart this install script. Repeat until PHP7 was successfully build.
# Example error: "configure: WARNING: This bison version is not supported for regeneration of the Zend/PHP parsers (found: none, min: 204, excluded: )".
# Solution: sudo apt-get install bison
# Example error: "configure: error: xml2-config not found. Please check your libxml2 installation."
# Solution: sudo apt-get install libxml2-dev
# etc. for every error encountered.
if (("$SKIP" < "7")) ; then
if ! ./buildconf
	then
	informRestart $1 $2 6
	exit
fi
fi

if (( "$SKIP" < "8" )) ; then
if ! ./configure --prefix=$INSTALL_PATH/php7/usr --with-config-file-path=$INSTALL_PATH/php7/usr/etc --enable-ast
	then
	informRestart $1 $2 7
	exit
fi
fi
# If make fails because of missing .h or .c files, then you encountered a bug of buildconf/configure.
# The solution is to manually look for the line inside the Makefile, which should produce the missing file. Use the specified command manually to build the missing file. Afterwards retry 'make'.
if (("$SKIP" < "9")) ; then
if ! make -j $CPUS
	then
	informRestart $1 $2 8
	exit
fi
fi

if (("$SKIP" < "10")) ; then
if ! make install
	then
	informRestart $1 $2 9
	exit
fi
fi

# Replace php7 php.ini with php.ini from phpjoern.
cp $1/phpjoern/conf/php.ini $1/php7/usr/etc/php.ini

# PHP7 install finished.
# Next: Install the Neo4j 2.1 graph database server.
if (("$SKIP" < "11")) ; then
if ! mkdir $NEO4J_BASEDIR
	then
	informRestart $1 $2 10
	exit
fi
fi

cd /tmp/

if (("$SKIP" < "12")) ; then
if ! curl -O http://neo4j.com/artifact.php?name=neo4j-community-2.1.8-unix.tar.gz
	then
	informRestart $1 $2 11
	exit
fi
fi

if (("$SKIP" < "13")) ; then
if ! tar xvfz artifact.php\?name=neo4j-community-2.1.8-unix.tar.gz
	then
	informRestart $1 $2 12
	exit
fi
fi

if (("$SKIP" < "14")) ; then
if ! mv neo4j-community-2.1.8 $NEO4J_BASEDIR/neo4j-01
	then
	informRestart $1 $2 13
	exit
fi
fi

# Next: Install the Gremlin plugin for Neo4j 2.1.
if (("$SKIP" < "15")) ; then
if ! git clone https://github.com/neo4j-contrib/gremlin-plugin
	then
	informRestart $1 $2 14
	exit
fi
fi

cd gremlin-plugin

if (("$SKIP" < "16")) ; then
if ! mvn clean package
	then
	informRestart $1 $2 15
	exit
fi
fi

if (("$SKIP" < "17")) ; then
if ! unzip target/neo4j-gremlin-plugin-2.1-SNAPSHOT-server-plugin.zip -d $NEO4J_BASEDIR/neo4j-01/plugins/gremlin-plugin
	then
	informRestart $1 $2 16
	exit
fi
fi

# Copy the neo4j installation to three other places, so that we can use four different neo4j instances at once.
cp -r $NEO4J_BASEDIR/neo4j-01 $NEO4J_BASEDIR/neo4j-02
cp -r $NEO4J_BASEDIR/neo4j-01 $NEO4J_BASEDIR/neo4j-03
cp -r $NEO4J_BASEDIR/neo4j-01 $NEO4J_BASEDIR/neo4j-04

# Next: Install batch-import 2.1 (should match neo4j version). 
# This is needed to import graph databases into neo4j 2.1.
if (("$SKIP" < "18")) ; then
if ! mkdir $INSTALL_PATH/batch-import
	then
	informRestart $1 $2 17
	exit
fi
fi

cd /tmp

if (("$SKIP" < "19")) ; then
if ! curl -O https://dl.dropboxusercontent.com/u/14493611/batch_importer_21.zip
	then
	informRestart $1 $2 18
	exit
fi
fi

if (("$SKIP" < "20")) ; then
if ! unzip batch_importer_21.zip -d $INSTALL_PATH/batch-import
	then
	informRestart $1 $2 19
	exit
fi
fi

# Get directory path of this script.
#SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install python-joern globally.
if (("$SKIP" < "21")) ; then
wget https://github.com/fabsx00/python-joern/archive/0.3.1.tar.gz
tar xfzv 0.3.1.tar.gz
cd python-joern-0.3.1
sudo python2 setup.py install
fi
# Utilities installation DONE.
# Configure ccdetection with installed paths.
if (("$SKIP" < "22")) ; then
if ! python $THIS_SCRIPT_DIR/main.py config -p $INSTALL_PATH
    then
    informRestart $1 $2 21
    exit
fi
fi

# Link neo4j databases
if (("$SKIP" < "23")) ; then
if ! ln -s $THIS_SCRIPT_DIR/graphs/graph1.db $NEO4J_BASEDIR/neo4j-01/data/graph.db || ! ln -s $THIS_SCRIPT_DIR/graphs/graph2.db $NEO4J_BASEDIR/neo4j-02/data/graph.db || ! ln -s $THIS_SCRIPT_DIR/graphs/graph3.db $NEO4J_BASEDIR/neo4j-03/data/graph.db || ! ln -s $THIS_SCRIPT_DIR/graphs/graph4.db $NEO4J_BASEDIR/neo4j-04/data/graph.db
    then
    informRestart $1 $2 22
    exit
fi
fi

echo "Installation finished! Start using ccdetection using 'python2 main.py help'"
