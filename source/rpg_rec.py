import math
import pyspark as ps
from pyspark.sql import SQLContext
from pyspark.mllib.recommendation import ALS

# create spark session
# use local[7] on ec2 instance
spark = ps.sql.SparkSession.builder.master('local[7]').appName('rpgrec').getOrCreate()

# load in the ratings data
df = spark.read.csv('../data/ratings.csv',
                       header=False,
                       sep='|',
                       inferSchema=True)
#  df.show()
'''
+---+---+---+
|_c0|_c1|_c2|
+---+---+---+
| 56|  0|  1|
'''

# convert to rdd...
data_rdd = df.rdd

# tarin/test sets...
training_RDD, validation_RDD, test_RDD = data_rdd.randomSplit([6, 2, 2])
validation_for_predict_RDD = validation_RDD.map(lambda x: (x[0], x[1]))
test_for_predict_RDD = test_RDD.map(lambda x: (x[0], x[1]))


# run a recommender...
# Parameters
seed = 5L
iterations = 10
regularization_parameter = 0.1
ranks = [a for a in xrange(4,30,2)]
errors = [0 for a in ranks]
err = 0
tolerance = 0.02
min_error = float('inf')
best_rank = -1
best_iteration = -1


for rank in ranks:
    last = ''
    try:
        last = 'model'
        model = ALS.train(training_RDD, rank, seed=seed, iterations=iterations, lambda_=regularization_parameter)
        last = 'predicions'
        predictions = model.predictAll(validation_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
        last = 'rates & predicions'
        rates_and_preds = validation_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
        last = 'errors'
        error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())
        errors[err] = error
        err += 1
        print 'For rank %s the RMSE is %s' % (rank, error)
        if error < min_error:
            min_error = error
            best_rank = rank
    except:
        print 'error at {} with rank {}'.format(last, rank)

print 'The best model was trained with rank %s' % best_rank

training_RDD, test_RDD = data_rdd.randomSplit([7, 3], seed=0L)

complete_model = ALS.train(training_RDD, best_rank, seed=seed,
                           iterations=iterations, lambda_=regularization_parameter)

test_for_predict_RDD = test_RDD.map(lambda x: (x[0], x[1]))

predictions = complete_model.predictAll(test_for_predict_RDD).map(lambda r: ((r[0], r[1]), r[2]))
rates_and_preds = test_RDD.map(lambda r: ((int(r[0]), int(r[1])), float(r[2]))).join(predictions)
error = math.sqrt(rates_and_preds.map(lambda r: (r[1][0] - r[1][1])**2).mean())

print 'For testing data the RMSE is %s' % (error)
