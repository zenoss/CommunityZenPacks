#!/bin/bash

die() {
	echo $*
	exit 1
}

try() {
	"$@"
	if [ $? -ne 0 ]; then
		echo "Command failure: $@"
		exit 1
	fi
}

if [ $# != 2 ]; then
	echo "Please specify python version to build for, and build file."
	exit 1
fi
if [ ! -e $2 ]; then
	echo "Specified file $2 does not exist."
	exit 1
fi
PKGDIR=/var/tmp/zenpacks
PYTHONVER=$1
if [ $PYTHONVER = "all" ]; then
	PYTHONVER="2.6 2.7"
fi
BUILDFILE="$(realpath $2)"
PV="$(basename $BUILDFILE)"
leftover="$(dirname $BUILDFILE)"
PN="$(basename $leftover)"
DEF_FILE=$leftover/defaults
leftover="$(dirname $leftover)"
CAT="$(basename $leftover)"
OUTPATH=$PKGDIR/$CAT/$PN
install -d $OUTPATH

echo "Building package $CAT/$PN version $PV"

TMPDIR=/var/tmp/pybuild/$CAT/$PN/$PV
CLONECACHE=/var/tmp/pybuild/cloned-repositories/$CAT/$PN

# source "defaults" file -- if it exists.
[ -e $DEF_FILE ] && . $DEF_FILE
# source build file
if [ ! -e "$BUILDFILE" ]; then
	echo "Please specify build file."
	exit 1
else
. $BUILDFILE
fi
if [ "$SRC_URI" = "" ]; then
	echo "Build file $BUILDFILE missing required variable SRC_URI."
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

rm -rf $TMPDIR
install -d $TMPDIR || die "Couldn't create temp dir: $TMPDIR"

prep_sources() {
	install -d $(dirname $CLONECACHE) || die
	cd $(dirname $CLONECACHE) || die
	if [ ! -d $CLONECACHE ]; then
		git clone $SRC_URI $(basename $CLONECACHE) || die "Couldn't clone git repository"
	else
		cd $CLONECACHE || die
		try git fetch
	fi
	S=$TMPDIR/$PN
	cd $TMPDIR || die "Couldn't change into TMPDIR" 
	cp -a $CLONECACHE . || die "Couldn't copy from clone cache"
	cd $S || die "Couldn't change into source directory"
	git checkout -q $COMMIT || die "Couldn't checkout specified commit: $COMMIT"
	echo "At commit $COMMIT"
}

build_zenpack() {
	# clean-up for repos with naughty things committed:
	rm -rf dist build
	# use a sanitized name rather than our ugly old namespace name:
	OUTFILE=$OUTPATH/$PN-$PV-py$PY.egg
	if [ -e $OUTFILE ]; then
		echo "$OUTFILE already exists, skipping build."
		return
	fi
	prep_sources
	if [ ! -e setup.py ]; then
		echo "setup.py does not exist. Cannot continue."
		exit 1
	else
		#rework setup.py from scratch
		sed -n -e '1,/STOP_REPLACEMENTS/p' setup.py > setup.py.new
		#tweak setup.py to include custom info from us:
		sed -i \
		-e "/^PREV_ZENPACK_NAME/d" \
		-e "s/^NAME[[:space:]]*=/PREV_ZENPACK_NAME=/" \
		-e "/^PREV_ZENPACK_NAME/a\NAME=\"$CAT/$PN\"" \
		-e "/^VERSION[[:space:]]*=/cVERSION=\"$PV\"" \
		setup.py.new || die "sed fail"
		# grab any custom package data
		pkgdata="$( sed -n -e '/^[[:space:]]*package_data/,/[}],/p' setup.py)"
		if [ -n "$pkgdata" ]; then
			# remove trailing comma
			echo "${pkgdata%,}" >> setup.py.new
		else
			echo "package_data = {}" >> setup.py.new
		fi
		cat >> setup.py.new << EOF
from setuptools import setup, find_packages

setup(
    name = NAME,
    version = VERSION,
    author = AUTHOR,
    license = LICENSE,
    compatZenossVers = COMPAT_ZENOSS_VERS,
    prevZenPackName = PREV_ZENPACK_NAME,
    namespace_packages = NAMESPACE_PACKAGES,
    packages = find_packages(),
    include_package_data = True,
    package_data = package_data,
    install_requires = INSTALL_REQUIRES,
    entry_points = { 'zenoss.zenpacks' : '%s = %s' % (PACKAGES[-1], PACKAGES[-1]) },
    zip_safe = False
)
EOF
		cat setup.py.new > setup.py || die
	fi
	$PYTHON setup.py bdist_egg || die "Couldn't build ZenPack"
	artifact="$(ls dist/*.egg)"
	if [ -e "$artifact" ]; then
		echo "Found artifact $artifact"
		cp $artifact $OUTFILE
		echo "Successfully built $OUTFILE."
	else
		pwd
		echo "Could not find egg build artifact. $artifact"
		exit 1
	fi
}

for PY in $PYTHONVER; do
	export PYTHON=python$PY
	which $PYTHON > /dev/null 2>&1
	if [ $? -ne 0 ]; then
		die "Could not find installed version of $PYTHON."
	fi
	build_zenpack $PY
done

