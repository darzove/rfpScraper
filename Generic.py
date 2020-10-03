import os
import pymongo
from pymongo.collection import BulkWriteError
from seleniumc.chrome import Chrome
from seleniumc.default import config
from datetime import datetime

config['BINARY_PATH'] = os.environ.get('CHROMEDRIVER')
if config['BINARY_PATH'] is None:
    raise Exception('CHROMEDRIVER path variable not set')

class Generic():
    def __init__(self, target):
        if not target:
            raise Exception("Please specify a target to scrape")

        self.home_path = os.path.dirname(__file__)
        self.c = self.setup()
        self.cli = pymongo.MongoClient('localhost', 27017)
        self.con = self.cli['iceCream']

        self.collection = 'solicitations'
        self.db = self.con[self.collection]

        if target == "emma":
            self.name = "emma"
            self.tableid = "body_x_grid_grd"
            self.homepage = 'https://emma.maryland.gov/page.aspx/en/rfp/request_browse_public'
        else:
            self.name = "periscope"
            self.tableid = "resultsTable"
            self.homepage = 'https://www.commbuys.com/bso/external/publicBids.sdo'

        self.batch_size = 50

        with open(os.path.join(self.home_path, 'scripts', f'{target}_stage1.js'), 'r') as f:
            self.rip_stage1 = f.read()
        with open(os.path.join(self.home_path, 'scripts', f'{target}_stage2.js'), 'r') as f:
            self.rip_stage2 = f.read()

    def setup(self):
        c = Chrome(config)
        #You may ignore this preload script - this is a home brewed script of 11 herbs and spices to minimize chances
        #that we will be detected as a bot
        with open(os.path.join(self.home_path, "scripts", 'preload.js'), 'r') as f:
            c.inject(f.read())
        return c

    #the goal with this is to gracefully pass over existing data which has been scraped, if you run it more than once
    def bulk_write(self, data):
        requests = [self.modify(i) for i in data]
        try:
            results = self.db.bulk_write(requests, ordered=False)
        except BulkWriteError as bwe:
            results = bwe.details
        return results

    def modify(self, doc):
        doc['datescraped'] = datetime.now().isoformat()
        return pymongo.InsertOne(doc)

    def stage1(self):
        self.c.get(self.homepage)

        while True:
            if not self.c.wait_for(self.tableid):
                raise Exception("Unable to find the table element")

            data = self.c.driver.execute_script(self.rip_stage1)
            self.bulk_write(data['rfps'])
            self.c.sleep()
            if not data['next']:
                break

    def stage2(self):
        while True:
            if self.db.count_documents({'origin': self.name, 'complete': False, 'error': False}) == 0:
                break

            for doc in self.db.find({'origin': self.name, 'complete': False, 'error': False}, batch_size=self.batch_size):
                try:
                    self.c.get(doc['link'])
                    data = self.c.driver.execute_script(self.rip_stage2)
                    self.db.update_one({'_id': doc['_id']}, {'$set': data})
                except:
                    self.db.update_one({'_id': doc['_id']}, {'$set': {'error': True}})

    def scrape(self):
        try:
            self.stage1()
            self.stage2()
        except:
            pass

        self.c.close()

if __name__ == "__main__":
    scraper = Generic("periscope")
    scraper.scrape()