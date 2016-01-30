#!/bin/bash

# This script can be used on debian based systems to install all tools necessary for the ccdetection to work.
# This includes phpjoern, python-joern, PHP7, the graph database neo4j version 2.1, its Gremlin-plugin, batch-import 2.1.
# Some tools need to be compiled on your system, so that autoconf and maven will be used. Furthermore, all dependencies for compilation need to be available on the system.
# If any compiling process exits with missing file errors, resolve its dependencies, comment out all successfully finished steps in this script and restart it to continue.

# DEPENDENCIES FOR THIS SCRIPT TO WORK:
# Java JDK (tested with OpenJDK 7)
# E.g. to install OpenJDK 7: sudo apt-get install openjdk-7-jdk

# Ctrl-C should kill complete process group.
trap "kill 0" SIGINT

function informRestart {
	echo "Install failed at step `expr $3 - 1`. Restart using following command:"
	echo "./install.sh $1 $2 `expr $3 - 1`"
}

if [ -z "$1" ]; then
	echo "Please specify a path to install all utilities to as first program argument. I.e. the base directory for all tools."
	exit
fi

if [ -z "$2" ]; then
	echo "Please specify the number of CPUs to use for multithreading as second program argument. It is needed to setup multiple graph databases for ccdetection to work in parallel, using all specified CPUs."
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

_CTR=0

echo "The install script asks for sudo privileges for some steps. These steps are:"
echo "apt-get update"
echo "apt-get install autoconf bison flex maven unzip libxml2-dev python-setuptools python-dev -y"
echo "(For python-joern 0.3.1) python2 setup.py install"

if (("$SKIP" == "$_CTR")) ; then
sudo apt-get update
# Following tools will be used to install everything:
sudo apt-get install autoconf bison flex maven unzip libxml2-dev python-setuptools python-dev -y

fi

cd $INSTALL_PATH

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
# Get the old phpjoern version.
if ! git clone https://github.com/tommiu/phpjoern_mirror.git phpjoern
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
# Copy extended PHP parser script into phpjoern
if ! cp $THIS_SCRIPT_DIR/AST_parser/src/Parser.php $INSTALL_PATH/phpjoern/src/Parser.php
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
# Copy extended PHP parser script into phpjoern
if ! cp $THIS_SCRIPT_DIR/AST_parser/src/util.php $INSTALL_PATH/phpjoern/src/util.php
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
# Get the old python-joern version.
if ! git clone https://github.com/tommiu/python-joern_mirror.git python-joern
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

cd python-joern

# Get PHPJoernSteps extension for python-joern.
#_CTR=`expr $_CTR + 1`
#if (("$SKIP" < "$_CTR")) ; then
#if ! git checkout portPHPJoern
#then
#	informRestart $1 $2 $_CTR
#	exit
#fi
#fi

cd $INSTALL_PATH

# Install custom gremlin steps for python-joern.
#_CTR=`expr $_CTR + 1`
#if (("$SKIP" < "$_CTR")) ; then
#if ! cp -r $THIS_SCRIPT_DIR/custom_gremlin_steps $INSTALL_PATH/python-joern/joern/phpjoernsteps/.
#then
#    informRestart $1 $2 $_CTR
#    exit
#fi
#fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
# Download PHP7 - ~160 MB
if ! mkdir php7
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

cd $INSTALL_PATH/php7

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! git clone https://git.php.net/repository/php-src.git
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

cd php-src

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
cd ext
if ! git clone https://github.com/nikic/php-ast.git ast
then
	informRestart $1 $2 $_CTR
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
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! ./buildconf
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! ./configure --prefix=$INSTALL_PATH/php7/usr --with-config-file-path=$INSTALL_PATH/php7/usr/etc --enable-ast
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

# If make fails because of missing .h or .c files, then you encountered a bug of buildconf/configure.
# The solution is to manually look for the line inside the Makefile, which should produce the missing file. Use the specified command manually to build the missing file. Afterwards retry 'make'.
# Example error: File Zend/zend_language_parser.y is missing.
# Find rule in Makefile, cd into dir 'Zend' and execute the make rule: bison -y -p zend -v -d /path_to_php/php7/php-src/Zend/zend_language_parser.y -o zend_language_parser.c
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! make -j $CPUS
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! make install
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

# Replace php7 php.ini with php.ini from phpjoern.
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! cp $1/phpjoern/conf/php.ini $1/php7/usr/etc/php.ini
then
    informRestart $1 $2 $_CTR
    exit
fi
fi

# PHP7 install finished.
# Next: Install the Neo4j 2.1 graph database server.
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! mkdir $NEO4J_BASEDIR
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

cd /tmp/

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! curl -O http://neo4j.com/artifact.php?name=neo4j-community-2.1.8-unix.tar.gz
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! tar xvfz artifact.php\?name=neo4j-community-2.1.8-unix.tar.gz
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! mv neo4j-community-2.1.8 $NEO4J_BASEDIR/neo4j-01
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

# Next: Install the Gremlin plugin for Neo4j 2.1.
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! git clone https://github.com/neo4j-contrib/gremlin-plugin
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

cd gremlin-plugin

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
# There were some problems with the maven license check of the Gremlin plugin - using -Dlicense.skip we can skip these checks.
if ! mvn clean package -Dlicense.skip=true
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! unzip target/neo4j-gremlin-plugin-2.1-SNAPSHOT-server-plugin.zip -d $NEO4J_BASEDIR/neo4j-01/plugins/gremlin-plugin
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

# Copy the neo4j installation to more places, so that we can use different neo4j instances when multithreading.
for i in `seq 2 $CPUS`;
do
    _CTR=`expr $_CTR + 1`
    if (("$SKIP" < "$_CTR")) ; then
    if ! cp -r $NEO4J_BASEDIR/neo4j-01 $NEO4J_BASEDIR/neo4j-0$i
    then
        informRestart $1 $2 $_CTR
        exit
    fi
    fi
done

# Next: Install batch-import 2.1 (should match neo4j version). 
# This is needed to import graph databases into neo4j 2.1.
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! mkdir $INSTALL_PATH/batch-import
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

cd /tmp

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! curl -O https://dl.dropboxusercontent.com/u/14493611/batch_importer_21.zip
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! unzip batch_importer_21.zip -d $INSTALL_PATH/batch-import
then
	informRestart $1 $2 $_CTR
	exit
fi
fi

# Get directory path of this script.
#SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install python-joern globally.
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! wget https://github.com/fabsx00/python-joern/archive/0.3.1.tar.gz
then
    informRestart $1 $2 $_CTR
    exit
fi
fi

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! tar xfzv 0.3.1.tar.gz
then
    informRestart $1 $2 $_CTR
    exit
fi
fi

cd python-joern-0.3.1

_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! sudo python2 setup.py install
then
    informRestart $1 $2 $_CTR
    exit
fi
fi

# Utilities installation DONE.
# Configure ccdetection with installed paths.
_CTR=`expr $_CTR + 1`
if (("$SKIP" < "$_CTR")) ; then
if ! python $THIS_SCRIPT_DIR/main.py config -p $INSTALL_PATH
then
    informRestart $1 $2 $_CTR
    exit
fi
fi

# Link neo4j databases
for i in `seq 1 $CPUS`;
do
    _CTR=`expr $_CTR + 1`
    if (("$SKIP" < "$_CTR")) ; then
    if ! ln -s $THIS_SCRIPT_DIR/graphs/graph${i}.db $NEO4J_BASEDIR/neo4j-0${i}/data/graph.db
    then
        informRestart $1 $2 $_CTR
        exit
    fi
    fi
done

echo "Installation finished!"
echo "Python dependencies were not installied. You will need the following python packages:"
echo "pexpect"
echo "Start using ccdetection with 'python2 main.py help'"
