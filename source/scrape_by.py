import time
import string
import random
import pymongo
import requests
import HTMLParser
from bs4 import BeautifulSoup


class Scraper(object):
    '''
    Grab users, find their product reviews, return the product ids.
    '''

    def __init__(self):
        # connect to the hosted MongoDB instance
        self.p2gs = {}
        self.mc = pymongo.MongoClient()  # Connect to the MongoDB server
        self.db = self.mc['driveby_rec']  # DataBase
        self.docs = self.db['docs']  # Use (or create) a collection called 'docs'

    def scrape(self):
        '''
        '''
        # try:
        cursor = self.docs.find({}).sort('cust_id', pymongo.DESCENDING).limit(1)
        last = 0
        for doc in cursor:
            last = int(doc['cust_id'])
            print(doc['cust_id'])

        # start a loop for the scraping...
        for cust_id in xrange(last + 1, 1368860):  # my ID.  Not including self
            print('{} \r'.format(cust_id)),
            lst = self.get_reviews(cust_id)
            for tup in lst:
                if len(lst) > 0:
                    time.sleep(random.randint(0,1)/100.0)
                    print(cust_id)
                # Store the document in MongoDB
                self.docs.insert_one({'cust_id': cust_id,
                                      'product_id': tup[0],
                                      'system': tup[1],
                                      'review': tup[2]})

    def get_rulesystem(self, n_prod):
        '''
        Return th Rules System for the given product number.
        '''
        try:
            ret = self.p2gs[n_prod]
        except:
            r = requests.get('http://www.drivethrurpg.com/product/{}'
                             .format(n_prod))
            soup = BeautifulSoup(r.content, 'html.parser')
            tags  = soup.find('ul', {'class':'rules-system-list'})
            # get it, clean it, and assign it
            ret = HTMLParser.HTMLParser().unescape(tags.get_text())
            self.p2gs[n_prod] = ret
        return ret

    def get_reviews(self, n_cust):
        '''
        find reviews by a given customer
        review links end in either the product_id or have '&it' after product id...
        other links mention cust_id and other things.
        <td valign="top" class="standardText standardContent">
        '''
        r = requests.get('http://www.drivethrurpg.com/product_reviews.php?' +
                         'customers_id={}'.format(n_cust))
        soup = BeautifulSoup(r.content, 'html.parser')
        tags  = soup.find_all('td', {'class':'standardText standardContent'})
        links = soup.find_all('a', href=True)
        lstl = []
        for link in links:
            if link['href'].find('products_id=') > 0:
                temp = link['href']
                temp = temp[temp.find('products_id=')+12:]
                try:
                    try:
                        temp = temp[:temp.index('&it')]
                    except:
                        pass
                    prod = int(temp)
                    lstl.append(prod)
                except:
                    pass
        lst_l = []
        for prod in lstl:
            if prod not in lst_l:
                lst_l.append(prod)
        lstr = []
        for tag in tags:
            lstr.append(''.join([a for a in tag.get_text()
                                 if a in string.printable]))
        ret = []
        for i, prod in enumerate(lst_l):
            try:
                ret.append((prod, self.get_rulesystem(prod), 'lstr[i]'))
            except:
                pass
        return ret

if __name__ == '__main__':
    scraper = Scraper()
    scraper.scrape()
