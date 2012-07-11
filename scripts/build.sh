#!/bin/bash

die() {
	echo $*
	exit 1
}

if [ ! -e "$1" ]; then
	echo "Please specify build file."
	exit 1
fi
. $1
if [ "$SRC_URI" = "" ]; then
	echo "Build file $1 missing required variable SRC_URI."
	exit 1
fi
if [ "$SRC_TYPE" != "git" ]; then
	echo "SRC_TYPE '$SRC_TYPE' not recognized. (Valid: 'git')"
	exit 1
fi
if [ "$COMMIT" = "" ]; then
	echo "COMMIT not specified."
	exit 1
fi
VERSION=$(basename $1)
TMPDIR=/var/tmp/pybuild/$1
rm -rf $TMPDIR
install -d $TMPDIR || die "Couldn't create temp dir: $TMPDIR"
cd $TMPDIR || die "Couldn't change into TMPDIR" 
git clone $SRC_URI || die "Couldn't clone git repository"

S=${SRC_URI##*/}
S=$TMPDIR/${S%.git}

cd $S || die "Couldn't change into source directory"
git checkout -q $COMMIT || die "Couldn't checkout specified commit: $COMMIT"
echo "At commit $COMMIT"

if [ ! -e setup.py ]; then
	echo "setup.py does not exist. Cannot continue."
	exit 1
fi

build_zenpack() {
	if [ $1 = "2.7" ]; then
		PYTHON=python2.7
	elif [ $1 = "2.6" ]; then
		PYTHON=python2.6
	fi
	
	# clean-up for repos with naughty things committed:
	rm -rf dist build
	python2.7 setup.py bdist_egg || die "Couldn't build ZenPack"
	artifact="$(ls dist/*.egg)"
	if [ -e "$artifact" ]; then
		echo "Found artifact $artifact"
	else
		pwd
		echo "Could not find egg build artifact. $artifact"
		exit 1
	fi
