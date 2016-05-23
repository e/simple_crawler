#!/usr/bin/python

import json
import requests
import re
import sys

from collections import OrderedDict
from hurry.filesize import size
from lxml import etree

HOST = 'hiring-tests.s3-website-eu-west-1.amazonaws.com'
PREFIX = 'http://'
URL = '/2015_Developer_Scrape/5_products.html'

XPATH_RESULT_LIST = '/html/body/div[1]/div[2]/div[1]/div[4]/div[2]/ul'
XPATH_PRODUCT_INFO = './/div[@class="productInfo"]//a'
XPATH_PRICE_DATA = './/p[@class="pricePerUnit"]'
XPATH_PRODUCT_TITLE = '//div[@class="productTitleDescriptionContainer"]/h1'
XPATH_DESCRIPTION = '//div[@class="productText"]'

GET_HEADERS = {
        'Host': HOST,
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        }


class Client:
    """
    Provides some methods to interact with Sainsbury's test website
    """
    def __init__(self):
        self. host = HOST
        self.baseurl = PREFIX + HOST
        self.url = self.baseurl + URL


    def get_data(self):
        '''
        This method gets some data and returns the JSON
        '''
        r = requests.get(self.url, headers=GET_HEADERS)
        html = etree.HTML(r.text)
        try:
            result_list = html.xpath(XPATH_RESULT_LIST)[0]
        except:
            raise Exception('Error parsing html. Have they changed the markup?')
        result = {'results': [], 'total': 0}
        for item in result_list:
            product_url = item.xpath(XPATH_PRODUCT_INFO)[0].attrib['href']
            product_response = requests.get(product_url, headers=GET_HEADERS)
            html = etree.HTML(product_response.text)
            response_len = product_response.headers['Content-Length']
            unit_price_data = res=html.xpath('.//p[@class="pricePerUnit"]')[0].text
            unit_price = re.search('\n\xa3([\d\.]+)', unit_price_data).groups(0)[0]
            title = html.xpath(XPATH_PRODUCT_TITLE)[0].text

            # For now it appears that the description is in the 1st
            # paragraph. There are four though, if they change that we'll
            # have to fix this
            description = html.xpath(XPATH_DESCRIPTION)[0].xpath('p')[0].text
            product_dict = OrderedDict()
            product_dict['title'] = title
            product_dict['size'] = size(int(response_len))
            product_dict['unit_price'] = unit_price
            product_dict['description'] = description
            result['results'].append(product_dict)
            result['total'] += float(unit_price)

        result['total'] = "%.2f" % result['total']
        return result


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print 'This script takes no arguments'
        sys.exit(1)
    else:
        c = Client()
        result = c.get_data()
        print(json.dumps(result, indent=4))
