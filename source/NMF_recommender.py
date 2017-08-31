import numpy as np
import pandas as pd
from math import sqrt
from scipy import sparse
from random import shuffle

class NMF_recommender(object):
    '''
    A Non-Negative Matrix Factorization recommender.
    Parameters:
        k - The number of latent features
        max_iter - number of iterations before the Factorization cancels out
        thresh - the threshold, how different the cost function needs to be in
                 in order to kick out of the iterations.
        l1 - lamba_1 in cost function
        l2 - lamba_2 in cost function
        verbose - set True to print out Cost Function during fitting

    Attributes:
        k - number of latent features
        iter - max_iter
        thresh - threshold paramater
        l1 - lamba_1
        l2 - lamba_2
    '''

    def __init__(self, k, max_iter=100, thresh=0.0001, l1=0.1, l2=0.1, verbose=False):
        '''
        Initializer.  See class for details.
        '''
        self.k = k
        self.thresh = thresh
        self.iter = max_iter
        self.l1 = l1
        self.l2 = l2
        self.verbose = verbose

    def fit(self, X):
        '''
        Fit function for the recommender system.
        Parameters:
            X - the utility-matrix we are trying to fit to

        Attributes:
            V - utility matrix in array form
            nonzero - a numpy array that is 1 where utility matrix is
                      nonzero and 0 otherwise
            b_star - how much users deviate from average
            b_prime - how much items deviate from average
            b_matrix - a matrix of b_stari - b_primej for all i,j
            cost - the cost function for a recommender
            W - User matrix
            H - Item Matrix
        '''
        # turn utility matrix to an arry
        self.V = X.toarray()
        nonzero = np.where(self.V > 0,1 ,0)
        k  = self.k

        # find mu...
        self.mu = np.sum(self.V)/np.count_nonzero(self.V)

        # find b_star & b_prime
        self.b_star = np.mean(self.V - self.mu*nonzero, axis=1)
        self.b_prime = np.mean(self.V - self.mu*nonzero, axis=0)

        # make b_matrix...
        # first, get a matrix of b_star as columns
        self.b_matrix =  np.column_stack((self.b_star for a in xrange(self.b_prime.shape[0])))
        # add to b_prime as rows...
        self.b_matrix = self.b_matrix + np.row_stack((self.b_prime for a in xrange(self.b_star.shape[0])))


        self.W = np.random.random_sample((self.V.shape[0], k))
        self.H = np.ones((k, self.V.shape[1]))
        if self.verbose:
            print 'Getting cost...'
        #cost function...
        Q = self.V - self.mu - self.b_matrix
        self.cost = (np.linalg.norm(Q - self.W.dot(self.H)) +
                         self.l1*(np.linalg.norm(self.W) + np.linalg.norm(self.H)) +
                         self.l2*(self.b_star.dot(self.b_star) + self.b_prime.dot(self.b_prime)))
        if self.verbose:
            print 'Cost starts at: {}'.format(self.cost)
        n = 0
        old_cost = self.cost + 2 * self.thresh
        I = np.identity(k)
        while (n < self.iter) and (abs(old_cost - self.cost) > self.thresh):
            if n % 2 == 0:
                self.H = np.linalg.lstsq(self.W + self.l1,
                                         Q + self.l2*self.b_matrix)[0]
                self.H[self.H < 0] = 0
            else:
                self.W = np.linalg.lstsq(self.H.T + self.l1,
                                         (Q + self.l2*self.b_matrix).T)[0].T
                self.W[self.W < 0] = 0
            old_cost = self.cost
            self.cost = (np.linalg.norm(Q - self.W.dot(self.H)) +
                         self.l1*(np.linalg.norm(self.W) +
                         np.linalg.norm(self.H)) +
                         self.l2*(self.b_star.dot(self.b_star) + self.b_prime.dot(self.b_prime)))
            n +=1
            if self.verbose:
                print "Iteration {}: Cost Difference = {}".format(n, abs(old_cost - self.cost))
        return self.W, self.H

    def predict(self):
        '''
        Get values for items.
        Attributes:
            ratings - The returned ratings
        '''
        self.ratings = self.mu + self.b_matrix + self.W.dot(self.H)
        return self.ratings

    def predict_cold(self, v):
        '''
         Fit function for the recommender system.
        Parameters:
            v - a list of tuples describing how user rated items,
                format [(item_1, rating_1), (item_2, rating_2), ..., (item_n, raing_n)]

        Attributes:
            ratings - The returned ratings for all the included users
        '''
        # make sure we have ratings
        try:
            ratings = self.ratings
        except:
            ratings = self.predict()
        pass

    def get_rmse(self, X_full):
        '''
        Assumes a training matrix with missing values was used, checks the values that are in
        X_full but not in self.V and calculates the RMSE.
        Parameters:
            X_full - the utility-matrix that vaules were removed from to get X in our fit

        Attributes:
            Xf - the full utility matric
            rmse - root mean squared error
        '''
         # make sure we have ratings
        ratings = self.predict()
        self.Xf = X_full.toarray()
        X_1 = np.where(self.Xf > 0, 1, 0)
        X_2 = np.where(self.V == 0, 0, 1)
        X_check = X_1 - X_2
        X_check[X_check <= 0] = 0
        self.rmse = sqrt(np.sum((self.Xf[X_check==1] - self.ratings[X_check==1])**2)/float(np.count_nonzero(X_check)))
        return self.rmse

if __name__ == '__main__':
    # first load my data...
    ratings = pd.read_csv('../data/ratings.csv', delimiter='|', header=None, names=['user_id', 'system_id', 'ratings'])

    # get highest user_id & highest system_id
    highest_user_id = ratings.user_id.max()
    highest_system_id = ratings.system_id.max()

    # make a sparse matrix...
    utility_matrix = sparse.lil_matrix((highest_user_id + 1,
                                        highest_system_id + 1))
    # +1 to be able to use actual ids, as opposed to having to make consessions

    # of course, now I need to fill it with ratings...
    for _, row in ratings.iterrows():
            utility_matrix[row.user_id, row.system_id] = row.ratings

    # Validation Set...
    train_utility_matrix = utility_matrix.copy()
    utility_dict = utility_matrix.todok(copy=False)
    lst = utility_dict.keys()
    shuffle(lst)
    cut = int(len(lst)*0.8)
    train = lst[:cut]
    hold_out = lst[cut:]

    # now remove hold_out
    for tup in hold_out:
        train_utility_matrix[tup] = 0

    for tup in hold_out[:5]:
        print utility_matrix[tup], train_utility_matrix[tup]

    # Grid search...
    ks = [a for a in range(5,35,5)]
    ls = [0.5*a for a in range(1, 5, 1)]
    best_k = 0
    best_l1 = 0
    best_l2 = 0
    best_rmse = 9001  # it's over 9000! (never saw that show)
    for k in ks:
        for l1 in ls:
            for l2 in ls:
                nmf = NMF_recommender(k=k, max_iter=51, thresh=1.0, l1=l1,
                                      l2=l2, verbose=False)
                nmf.fit(train_utility_matrix)
                rmse = nmf.get_rmse(utility_matrix)
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_k = k
                    best_l1 = l1
                    best_l2 = l2
                print('RMSE = {} for k={}, l1={}, l2={}'.format(rmse, k, l1,
                                                                l2))
    print()
    print('Best params are k={}, l1={}, l2={}'.format(best_k, best_l1, best_l2))
