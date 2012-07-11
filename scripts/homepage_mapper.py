#!/usr/bin/env python

'''
Created on Jun 25, 2012

@author: David Petzel

A little utility to easy the pain of initially creating homepage attribute in default files
'''
import httplib
import re
import logging
from pprint import pprint
import time

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Amount of seconds to sleep between page fetches
#so we don't toast jive by accident
JIVE_SLEEP_SAVER = 0

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
        self._find_pack_file_name()

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
                    pack_title = matches.group("pack_name")
                    if pack_title not in self.jive_page_map:
                        self.jive_page_map[pack_title] = {}
                    self.jive_page_map[pack_title]['home_page_url'] = \
                        matches.group("pack_page")
                    #print matches.group("pack_name"), " --- ", matches.group("pack_page")

    def _find_pack_file_name(self):
        """
        Using the jump page or other home page, try and determine what the
        zenpack file name is
        """
        for pack_title, pack_data in self.jive_page_map.items():
            if 'home_page_url' not in pack_data:
                #Not enough info
                continue
            home_page_url = pack_data['home_page_url']
            logger.info("Looking for pack name of {0} in {1}".format(
                                                pack_title, home_page_url))
            logger.debug("Giving Jive a {0} second breather".format(
                                                            JIVE_SLEEP_SAVER))
            time.sleep(JIVE_SLEEP_SAVER)
            #Hit each page and try to find it
            conn = httplib.HTTPConnection(self.jive_host)
            conn.request("GET", home_page_url)
            r1 = conn.getresponse()
            if r1.status != 200: continue
            page_data = r1.read()
            #Using the page data, try and extract a file name
            file_name_pattern = "(?i)(zenpacks\..*?)(\s|-|\"|\<|/)"
            matches = re.findall(file_name_pattern, page_data)
            for match in matches:
                if not match[0].startswith("zenpacks.zenoss.org"):
                    self.jive_page_map[pack_title]['pack_name'] = \
                        match[0]
                    break


if __name__ == '__main__':
    mapper = HomepageMapper()
    mapper.do_map()
   	
