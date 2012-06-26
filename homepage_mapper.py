'''
Created on Jun 25, 2012

@author: David Petzel

A little utility to easy the pain of initially creating homepage attribute in default files
'''
import httplib
import re
import logging
from pprint import pprint

logging.basicConfig()
logger=logging.getLogger()

class HomepageMapper(object):
    """
    Class to do the work
    """
    
    def __init__(self):
        self.jive_host = "community.zenoss.org"
        self.jive_url = "/community/zenpacks"
        self.jive_page_map = {}
        
    def do_map(self):
        """
        The externally callable method to get the ball rolling
        """
        self._fetch_zenpack_listing()
        
        pprint(self.jive_page_map)
    
    def _fetch_zenpack_listing(self):
        """
        Fetch the listing of Zenpacks from the community jive site
        """
        conn = httplib.HTTPConnection(self.jive_host)
        conn.request("GET", self.jive_url)
        r1 = conn.getresponse()
        if r1.status != 200:
            logger.critical("Failed to fetch zenpack list")
            exit(1)
        
        #From a 200 response, read the data    
        data1 = r1.read()
        
        
        
        ##pattern = '<tr><td.*?href="(?P<jive_url>.*?)">(?P<pack_name>.*?)</a>.*?<td.*?href="(?P<pack_author>.*?)">.*?</tr>'
        #Grab each table row first
        rows = re.findall("<tr>.*?</tr>", data1)
        for row in rows:
            #Now grab each column in the row
            columns = re.finditer("<td.*?>(?P<pack_column>.*?)</td><td.*?>(?P<author_column>.*?)</td>.*?", row)
            for column in columns:
                #Break it down further
                matches = re.search("href=\"(?P<pack_page>.*?)\">(?P<pack_name>.*?)</a>", column.group("pack_column"))
                if matches is not None:
                    self.jive_page_map[matches.group("pack_name")] = matches.group("pack_page")
                    #print matches.group("pack_name"), " --- ", matches.group("pack_page")
        

if __name__ == '__main__':
    mapper = HomepageMapper()
    mapper.do_map()