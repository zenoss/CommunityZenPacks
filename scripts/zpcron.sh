#!/bin/bash
mydir=$(dirname $(readlink -f $0))
echo $mydir
$mydir/zpparse && $mydir/zpbuild
