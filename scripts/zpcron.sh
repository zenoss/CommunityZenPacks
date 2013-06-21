#!/bin/bash
mydir=$(dirname $(readlink -f $0))
cd $mydir
$mydir/zpparse-ng && $mydir/zpbuild-ng 2>&1 | tee ~/zprepo-ng/zpbuild.txt
