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

zprepo = os.path.join(os.path.expanduser("~"), "zprepo")
zptemp = "/var/tmp/zpbuild"
zpconf = zptemp + "/etc"
zpdefs = zpconf + "/zpdefs.xml"
builddefs = zpconf + "/builddefs.xml"
if not os.path.exists(zpconf):
	os.makedirs(zpconf)
