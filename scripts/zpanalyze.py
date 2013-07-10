#!/usr/bin/python2
import fnmatch, os, re, stat, glob
from lxml import etree

# These locate* functions are all recursive file-finding functions:

def locate(path, fnpattern="", ignore=[]):
	for root, dirnames, filenames in os.walk(path):
		for filename in fnmatch.filter(filenames, fnpattern):
			if filename not in ignore:
				yield os.path.join(root, filename)
def locate_py(path):
	return locate(path, fnpattern="*.py", ignore=["__init__.py"])

def locate_zcml(path):
	return locate(path, fnpattern="*.zcml")

def locate_xml(path):
	return locate(path, fnpattern="*.xml")

def scanFileForElement(fn, target):
	a = open(fn,'rb')
	root = etree.parse(a)
	a.close()
	for el in root.iter('{*}%s' % target):
		yield el 

def scanFileForRegex(fn, expression):
	a = open(fn, 'r')
	r = re.compile(expression)
	found = False
	for l in a.readlines():
		if r.search(l):
			found = True
			break
	a.close()
	return found

class zpComplexity(object):

	def __init__(self, path, zpname):
		self.path = path
		self.zpname = zpname
		self.tags = set()
		self.all_tags = set([
			"BasicConfig",
			"EventTransforms",
			"CommandPlugins",
			"Scripts",
			"Datasources",
			"ModelerPlugins",
			"UI",
			"ModelExtensions",
			"APIs",
			"CollectorDaemons",
			"HubServices",
			"Impact",
			"Analytics",
			"UnitTests"])
		self.zp_path = os.path.join(os.path.normpath(path), os.path.sep.join(zpname.split(".")))

	def sanityCheck(self):
		if not os.path.exists(self.zp_path):
			# Couldn't find ZenPack directory - something is wrong
			return None
	
	def basicConfigTest(self):
		p = os.path.join(self.zp_path, "objects")
		if os.path.exists(p):
			for f in locate_xml(p):
				for el in scanFileForElement(f, "object"):
					self.tags.add("BasicConfig")
					return

	def eventTransformsTest(self):
		p = os.path.join(self.zp_path, "objects")
		if os.path.exists(p):
			for f in locate_xml(p):
				for el in scanFileForElement(f, "object"):
					if el.get("class") == "EventClassInst":
						for p in el.iter("{*}property"):
							if p.get("id") == "transform":
								self.tags.add("EventTransforms")
								return
	def commandPluginsTest(self):
		p = os.path.join(self.zp_path, "objects")
		if os.path.exists(p):
			for f in locate_xml(p):
				for el in scanFileForElement(f, "object"):
					if el.get("class")  == "BasicDataSource":
						for p in el.iter("{*}property"):
							if p.get("id") == "sourcetype":
								if p.text.strip() == "COMMAND":
									self.tags.add("CommandPlugins")
									return

	def scriptsTest(self):
		p = os.path.join(self.zp_path, "bin")
		if os.path.exists(p):
			for x in os.listdir(p):
				xf = os.path.join(p,x)
				if os.path.isfile(xf):
					st = os.stat(xf)
					if st.st_mode & stat.S_IEXEC:
						self.tags.add("Scripts")
						return
	
	def datasourcesTest(self):
		p = os.path.join(self.zp_path, "datasources")
		if os.path.exists(p):
			for f in glob.glob("%s/*.py" % p):
				bf = os.path.basename(f)
				if bf == "__init__.py":
					continue
				classname = bf[:-3]
				if scanFileForRegex(f, "^class %s\(" % classname):
					self.tags.add("Datasources")
					return

	def modelerPluginsTest(self):
		p = os.path.join(self.zp_path, "modeler/plugins")
		if os.path.exists(p):
			for f in locate_py(p):
				bf = os.path.basename(f)
				classname = bf[:-3]
				if scanFileForRegex(f, "^class %s\(" % classname):
					self.tags.add("ModelerPlugins")
					return
	def UITest(self):
		for f in locate_zcml(self.zp_path):
			if not scanFileForElement(f, 'resourceDirectory'):
				if not scanFileForElement(f, 'viewlet'):
					continue
			self.tags.add("UI")
			return
	
	def modelExtensionsTest(self):
		for f in glob.glob("%s/*.py" % self.zp_path):
			if scanFileForRegex(f, 'Products\.ZenModel\.(Device|DeviceComponent|ManagedEntity|HWComponent|OSComponent|FileSystem|IpInterface|OSProcess|CPU|PowerSupply|TemperatureSensor|Fan|ExpansionCard|HardDisk|IpService|WinService|Software)'):
				self.tags.add("ModelExtensions")
				return
	
	def APIsTest(self):
		for f in locate_py(self.zp_path):
			if scanFileForRegex(f, '^class [^\(]+\(.*?ZuulFacade'):
				self.tags.add("APIs")
				return

	def collectorDaemonsTest(self):
		p = os.path.join(self.zp_path, "daemons")
		if os.path.exists(p):
			for x in os.listdir(p):
				xf = os.path.join(p,x)
				if os.path.isfile(xf):
					st = os.stat(xf)
					if st.st_mode & stat.S_IEXEC:
						self.tags.add("CollectorDaemons")
						return
	
	def hubServicesTest(self):
		p = os.path.join(self.zp_path, "services")
		if os.path.exists(p):
			for f in glob.glob("%s/*.py" % p):
				bf = os.path.basename(f)
				if bf == "__init__.py":
					continue
				self.tags.add("HubServices")
				return

	def impactTest(self):
		my_attrs = [ 
			"ZenPacks.zenoss.Impact.impactd.interfaces.IRelationshipDataProvider",
			"ZenPacks.zenoss.Impact.impactd.interfaces.INodeTriggers", 
			"ZenPacks.zenoss.Impact.stated.interfaces.IStateProvider" 
		]
		for f in locate_zcml(self.zp_path):
			for el in scanFileForElement(f, "subscriber"):
				if el.get("provides") in my_attrs:
					self.tags.add("Impact")
					return
	def analyticsTest(self):
		for f in locate_zcml(self.zp_path):
			for el in scanFileForElement(f, "subscriber"):
				if el.get("provides") == "Products.Zuul.interfaces.IReportableFactory":
					self.tags.add("Impact")
					return
			for el in scanFileForElement(f, "adapter"):
				if el.get("provides") == "Products.Zuul.interfaces.IReportable":
					self.tags.add("Impact")
					return

	def unitTestsTest(self):
		p = os.path.join(self.zp_path, "tests")
		if os.path.exists(p):
			for f in locate_py(p):
				if os.path.basename(f) == "testExample.py":
					continue
				self.tags.add("UnitTests")
				return

	def run(self):
		self.sanityCheck()
		self.basicConfigTest()
		self.eventTransformsTest()
		self.commandPluginsTest()
		self.scriptsTest()
		self.datasourcesTest()
		self.modelerPluginsTest()
		self.UITest()
		self.modelExtensionsTest()
		self.APIsTest()
		self.collectorDaemonsTest()
		self.hubServicesTest()
		self.impactTest()
		self.analyticsTest()
		self.unitTestsTest()

if __name__ == "__main__":
	import sys
	zpa = zpComplexity(sys.argv[1], sys.argv[2])
	zpa.run()
	print zpa.tags
	print zpa.all_tags - zpa.tags
