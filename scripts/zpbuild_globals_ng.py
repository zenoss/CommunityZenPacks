#!/usr/bin/env python2

import os

build_targets = ( 
	"Zenoss Core 3.2.x" ,
	"Zenoss Resource Manager 4.1.x" ,
	"Zenoss Core 4.2.x" 
)

python_targets = {
	"Zenoss Core 3.2.x" : "2.6",
	"Zenoss Resource Manager 4.1.x" : "2.7",
	"Zenoss Core 4.2.x" : "2.7"
}

zprepo = os.path.join(os.path.expanduser("~"), "zprepo-ng")
zptemp = "/var/tmp/zpbuild-ng"
zpconf = zptemp + "/etc"
zpdef_file = zpconf + "/zpdefs.json"
reldef_file = zpconf + "/reldefs.json"
builddefs = zpconf + "/builddefs.json"
if not os.path.exists(zpconf):
	os.makedirs(zpconf)
