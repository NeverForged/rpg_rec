import csv
import pymongo
import cPickle as pickle


class Data(object):
    '''
    Class to interact with pymongo
    '''

    def __init__(self):
        # connect to the hosted MongoDB instance
        self.p2gs = {}
        self.mc = pymongo.MongoClient()  # Connect to the MongoDB server
        self.db = self.mc['driveby_rec']  # DataBase
        self.docs = self.db['docs']  # Use (or create) a collection called 'docs'

    def user_dict(self):
        '''
        To match the formatting of the files from a sample of how to use spark
        to build a movie recommender, I will create a dictionary of users,
        and each will be a dictionary of systems, where the answer is the
        number of reviews for that system by that user.
        '''
        # dictionaries...
        try:
            self.user = pickle.load(open('../dictionary/user.pickle', 'rb'))
        except:
            self.user = {}
            cursor = self.docs.find({}).sort('cust_id')
            for doc in cursor:
                u = doc['cust_id']
                s = doc['system']
                # should be a zero unless we have an answer...
                try:
                    self.user[u][s] = self.user[u][s] + 1
                except:
                    try:
                        self.user[u][s] = 1
                    except:
                        self.user[u] = {}
                        self.user[u][s] = 1
            # save it in case we need it later...
            with open('../dictionary/user.pickle', 'wb') as handle:
                    pickle.dump(self.user, handle,
                                protocol=pickle.HIGHEST_PROTOCOL)

    def dd(self):
        return defaultdict(int)

    def make_csv(self):
        '''
        Use the above dictionary to make a csv with the following format:

            cust_id | system name | ratings(#)

        This gives a number of times the user has rated a product in the given
        system.
        '''
        out = csv.writer(open("../data/ratings.csv","wb"), delimiter='|')
        self.user_dict()
        for cid in self.user.keys():
            for sys in self.user[cid].keys():
                out.writerow([cid, sys, self.user[cid][sys]])

if __name__ == '__main__':
    data = Data()
    data.make_csv()
