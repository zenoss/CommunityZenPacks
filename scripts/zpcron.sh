#!/bin/bash
mydir=$(dirname $(readlink -f $0))
cd $mydir
$mydir/zpparse && $mydir/zpbuild 2>&1 | tee ~/zprepo/zpbuild.txt
