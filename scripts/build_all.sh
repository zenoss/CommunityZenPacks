#!/bin/bash
if [ ! -d $1/profiles ]; then
	echo "Please specify path to root of ZenPack repository as first argument."
	exit 1
fi

for CAT in $(cat $1/profiles/categories); do
	for PN in $(ls $CAT); do
		for PV in $(ls $CAT/$PN); do
			[ $PV = "defaults" ] && continue
			echo $CAT/$PN/$PV
			scripts/build.sh 2.7 $CAT/$PN/$PV
		done
	done
done
