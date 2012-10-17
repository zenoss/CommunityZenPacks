#!/bin/bash

die() {
	echo $*
	exit 2
}

try() {
	"$@"
	if [ $? -ne 0 ]; then
		echo "Command failure: $@"
		exit 2
	fi
}

PKGDIR=$ZPREPO/zenpacks/
install -d $PKGDIR
TMPDIR=$ZPTEMP/build/$ZENPACK_NAME
CLONECACHE=$ZPTEMP/cloned-repositories/$ZENPACK_NAME

if [ "$SRC_URI" = "" ]; then
	echo "Missing required variable SRC_URI."
	exit 2
fi
if [ "$TAG" = "" ]; then
	echo "TAG not specified."
	exit 2
fi
if [ "$PYTHON_VERSION" = "" ]; then
	echo "Missing required variable PYTHON_VERSION."
	exit 2
fi

export PYTHON=python$PYTHON_VERSION
which $PYTHON > /dev/null 2>&1
if [ $? -ne 0 ]; then
	die "Could not find installed version of $PYTHON."
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
	S=$TMPDIR/$ZENPACK_NAME
	cd $TMPDIR || die "Couldn't change into TMPDIR" 
	cp -a $CLONECACHE . || die "Couldn't copy from clone cache"
	cd $S || die "Couldn't change into source directory"
	git checkout -q $TAG || die "Couldn't checkout specified tag: $TAG"
	echo "At tag $TAG"
	# clean-up for repos with naughty things committed:
	rm -rf dist build
}

build_zenpack() {
	echo "Starting build of $ZENPACK_NAME ($TITLE) version $VERSION for Python version $PYTHON_VERSION"
	echo
	# use a sanitized name rather than our ugly old namespace name:
	OUTFILE=$PKGDIR/$ZENPACK_NAME/$ZENPACK_NAME-$VERSION-py$PYTHON_VERSION.egg
	install -d "$(dirname $OUTFILE)"
	if [ -e $OUTFILE ]; then
		echo "$OUTFILE already exists, skipping build."
		exit 1
	fi
	prep_sources
	if [ ! -e setup.py ]; then
		die "setup.py does not exist. Cannot continue."
	else
		# grab version from our metadata, in case ZenPack author forgot to update it:
		sed -i \
			-e "/^VERSION[[:space:]]*=/cVERSION=\"$VERSION\"" \
			setup.py || die "sed fail"
	fi
	$PYTHON setup.py bdist_egg || die "Couldn't build ZenPack"
	artifact="$(ls dist/*.egg)"
	if [ -e "$artifact" ]; then
		echo "Found artifact $artifact"
		cp $artifact $OUTFILE
		echo "Successfully built $OUTFILE."
	else
		pwd
		die "Could not find egg build artifact. $artifact"
	fi
	rm -rf $TMPDIR
	exit 0
}

build_zenpack
