# This file keeps NaiveBayes outside of the pipelines to measure separate runtime
import sys
import time
import numpy as np
import scipy as sp
from scipy.sparse import csr_matrix
import scipy
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark import StorageLevel
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import Normalizer, StringIndexer
from pyspark.ml.feature import OneHotEncoder, QuantileDiscretizer
from pyspark.ml.feature import VectorAssembler, FeatureHasher
from pyspark.ml import Pipeline 
from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import math
import warnings

def readNprep():
    # Read the dataset
    path = sys.argv[1]
    criteo = spark.read.options(inferSchema='True', delimiter=',').csv(f"file:{path}")
    #print(criteo.printSchema())
    print("#partitions: ", criteo.rdd.getNumPartitions())
    criteo.persist(StorageLevel.MEMORY_ONLY)
    #print((criteo.count(), len(criteo.columns)))
    return criteo

def applyFTset1(criteo, nBins, nb_time):
    # Bin the numerical columns
    outCols = ['{0}_bin'.format(out) for out in criteo.columns[1:14]]
    newCols = outCols
    binner = QuantileDiscretizer(inputCols=criteo.columns[1:14], \
            outputCols=outCols, handleInvalid="skip", numBuckets=nBins)
    # Recode the categorical columns
    outCols = ['{0}_rc'.format(out) for out in criteo.columns[14:40]]
    newCols = newCols + outCols
    indexer = StringIndexer(inputCols=criteo.columns[14:40], outputCols=outCols, handleInvalid="skip")
    # Assemble the encoded columns the for the downstream trainer
    assembler = VectorAssembler(inputCols=newCols, outputCol='features', handleInvalid="keep")
    # Make a pipeline and apply
    pipe = Pipeline(stages=[binner, indexer, assembler])
    assembled = pipe.fit(criteo).transform(criteo)
    # Split the data into train and test
    splits = assembled.randomSplit([0.8, 0.2], 1234)
    train = splits[0]
    test = splits[1]
    # Train with Naive Bayes
    t1 = time.time()
    nb = NaiveBayes(smoothing=1.0, modelType="multinomial", featuresCol='features', labelCol='_c0')
    model = nb.fit(train)
    predictions = model.transform(test)
    # Calculate accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol='_c0', predictionCol='prediction',
            metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test set accuracy = " + str(accuracy))
    nb_time = nb_time + ((time.time() - t1) * 1000) #millisec
    print("Elapsed time for NB prediction = %s sec" % (time.time() - t1))
    return nb_time

def applyFTset2(criteo, nBins, nb_time):
    # Bin the numerical columns
    outCols = ['{0}_bin'.format(out) for out in criteo.columns[1:14]]
    newCols = outCols
    binner = QuantileDiscretizer(inputCols=criteo.columns[1:14], \
            outputCols=outCols, handleInvalid="skip", numBuckets=nBins)
    # Recode and dummycode the categorical columns
    outCols = ['{0}_rc'.format(out) for out in criteo.columns[14:40]]
    newCols = newCols + outCols
    indexer = StringIndexer(inputCols=criteo.columns[14:40], outputCols=outCols, handleInvalid="skip")
    outCols = ['{0}_dc'.format(out) for out in indexer.getOutputCols()]
    newCols = newCols + outCols
    one_hot = OneHotEncoder(dropLast=False, inputCols=indexer.getOutputCols(), outputCols=outCols)
    # Assemble the encoded columns the for the downstream trainer
    assembler = VectorAssembler(inputCols=newCols, outputCol='features', handleInvalid="keep")
    # Make a pipeline and apply
    pipe = Pipeline(stages=[binner, indexer, one_hot, assembler])
    assembled = pipe.fit(criteo).transform(criteo)
    # Split the data into train and test
    splits = assembled.randomSplit([0.8, 0.2], 1234)
    train = splits[0]
    test = splits[1]
    # Train with Naive Bayes
    t1 = time.time()
    nb = NaiveBayes(smoothing=1.0, modelType="multinomial", featuresCol='features', labelCol='_c0')
    model = nb.fit(train)
    predictions = model.transform(test)
    # Calculate accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol='_c0', predictionCol='prediction',
            metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test set accuracy = " + str(accuracy))
    nb_time = nb_time + ((time.time() - t1) * 1000) #millisec
    print("Elapsed time for NB prediction = %s sec" % (time.time() - t1))
    return nb_time

def applyFTset3(criteo, nBins, nb_time):
    # Bin the numerical columns
    outCols = ['{0}_bin'.format(out) for out in criteo.columns[1:14]]
    newCols = outCols
    binner = QuantileDiscretizer(inputCols=criteo.columns[1:14], \
            outputCols=outCols, handleInvalid="skip", numBuckets=nBins)
    # Feature hash the categorical columns
    newCols = newCols + ["hashed"]
    hasher = FeatureHasher(numFeatures=1000, inputCols=criteo.columns[14:40], outputCol="hashed")
    # Assemble the encoded columns the for the downstream trainer
    assembler = VectorAssembler(inputCols=newCols, outputCol='features', handleInvalid="keep")
    # Make a pipeline and apply
    pipe = Pipeline(stages=[binner, hasher, assembler])
    assembled = pipe.fit(criteo).transform(criteo)
    # Split the data into train and test
    splits = assembled.randomSplit([0.8, 0.2], 1234)
    train = splits[0]
    test = splits[1]
    # Train with Naive Bayes
    t1 = time.time()
    nb = NaiveBayes(smoothing=1.0, modelType="multinomial", featuresCol='features', labelCol='_c0')
    model = nb.fit(train)
    predictions = model.transform(test)
    # Calculate accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol='_c0', predictionCol='prediction',
            metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test set accuracy = " + str(accuracy))
    nb_time = nb_time + ((time.time() - t1) * 1000) #millisec
    print("Elapsed time for NB prediction = %s sec" % (time.time() - t1))
    return nb_time

def applyFTset4(criteo, nBins, nb_time):
    # Bin the numerical columns
    outCols = ['{0}_bin'.format(out) for out in criteo.columns[1:14]]
    newCols = outCols
    binner = QuantileDiscretizer(inputCols=criteo.columns[1:14], \
            outputCols=outCols, handleInvalid="skip", numBuckets=nBins)
    # Recode and dummycode the binned and recoded columns
    outCols = ['{0}_rc'.format(out) for out in criteo.columns[14:40]]
    newCols = newCols + outCols
    indexer = StringIndexer(inputCols=criteo.columns[14:40], outputCols=outCols, handleInvalid="skip")
    inCols = binner.getOutputCols() + indexer.getOutputCols() 
    outCols = ['{0}_dc'.format(out) for out in inCols]
    newCols = newCols + outCols
    one_hot = OneHotEncoder(dropLast=False, inputCols=inCols, outputCols=outCols)
    # Assemble the encoded columns the for the downstream trainer
    assembler = VectorAssembler(inputCols=newCols, outputCol='features', handleInvalid="keep")
    # Make a pipeline and apply
    pipe = Pipeline(stages=[binner, indexer, one_hot, assembler])
    assembled = pipe.fit(criteo).transform(criteo)
    # Split the data into train and test
    splits = assembled.randomSplit([0.8, 0.2], 1234)
    train = splits[0]
    test = splits[1]
    # Train with Naive Bayes
    t1 = time.time()
    nb = NaiveBayes(smoothing=1.0, modelType="multinomial", featuresCol='features', labelCol='_c0')
    model = nb.fit(train)
    predictions = model.transform(test)
    # Calculate accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol='_c0', predictionCol='prediction',
            metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test set accuracy = " + str(accuracy))
    nb_time = nb_time + ((time.time() - t1) * 1000) #millisec
    print("Elapsed time for NB prediction = %s sec" % (time.time() - t1))
    return nb_time

def applyFTset5(criteo, nBins, nb_time):
    # Bin the numerical columns
    outCols = ['{0}_bin'.format(out) for out in criteo.columns[1:14]]
    newCols = outCols
    binner = QuantileDiscretizer(inputCols=criteo.columns[1:14], \
            outputCols=outCols, handleInvalid="skip", numBuckets=nBins)
    # Recode and Feature hash the categorical columns
    outCols = ['{0}_rc'.format(out) for out in criteo.columns[14:26]]
    newCols = newCols + outCols
    indexer = StringIndexer(inputCols=criteo.columns[14:26], outputCols=outCols, handleInvalid="skip")
    newCols = newCols + ["hashed"]
    hasher = FeatureHasher(numFeatures=1000, inputCols=criteo.columns[26:40], outputCol="hashed")
    # Assemble the encoded columns the for the downstream trainer
    assembler = VectorAssembler(inputCols=newCols, outputCol='features', handleInvalid="keep")
    # Make a pipeline and apply
    pipe = Pipeline(stages=[binner, indexer, hasher, assembler])
    assembled = pipe.fit(criteo).transform(criteo)
    # Split the data into train and test
    splits = assembled.randomSplit([0.8, 0.2], 1234)
    train = splits[0]
    test = splits[1]
    # Train with Naive Bayes
    t1 = time.time()
    nb = NaiveBayes(smoothing=1.0, modelType="multinomial", featuresCol='features', labelCol='_c0')
    model = nb.fit(train)
    predictions = model.transform(test)
    # Calculate accuracy
    evaluator = MulticlassClassificationEvaluator(labelCol='_c0', predictionCol='prediction',
            metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)
    print("Test set accuracy = " + str(accuracy))
    nb_time = nb_time + ((time.time() - t1) * 1000) #millisec
    print("Elapsed time for NB prediction = %s sec" % (time.time() - t1))
    return nb_time


# NOTE: single-threaded execution takes 3.7x more time
spark = SparkSession\
    .builder\
    .master("local[32]")\
    .config("spark.driver.memory", "130g")\
    .config("spark.kryoserializer.buffer.max", "1024m")\
    .config("spark.sql.execution.arrow.pyspark.enabled", "true")\
    .appName("KddByMLlib")\
    .getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

criteo = readNprep()

timers = np.zeros(6)
ft_time = 0
nb_time = 0

# Bin(13) w/ 10 bins, RC(26) --> Total: 92.3s, NB: 62s
t1 = time.time()
nb_time = applyFTset1(criteo, 10, nb_time)
ft_time = ft_time + ((time.time() - t1) * 1000) #millisec
print("Elapsed time for fe1 = %s sec" % (time.time() - t1))

# Bin(13) w/ 5 bins, RC(26) --> Total: 81.5s, NB: 66s
t1 = time.time()
nb_time = applyFTset1(criteo, 5, nb_time)
ft_time = ft_time + ((time.time() - t1) * 1000) #millisec
print("Elapsed time for fe2 = %s sec" % (time.time() - t1))

# Bin(13) w/ 5 bins, DC(26) --> Total: 348.5s, NB: 320s
t1 = time.time()
nb_time = applyFTset2(criteo, 5, nb_time)
ft_time = ft_time + ((time.time() - t1) * 1000) #millisec
print("Elapsed time for fe4 = %s sec" % (time.time() - t1))

# Bin(13) w/ 10 bins, FH(26) --> Total: 27.5s, NB: 22s
t1 = time.time()
nb_time = applyFTset3(criteo, 10, nb_time)
ft_time = ft_time + ((time.time() - t1) * 1000) #millisec
print("Elapsed time for fe3 = %s sec" % (time.time() - t1))

# Bin(13) w/ 5 bins, DC(39) --> Total: 333s, NB: 301.3s
t1 = time.time()
nb_time = applyFTset4(criteo, 5, nb_time)
ft_time = ft_time + ((time.time() - t1) * 1000) #millisec
print("Elapsed time for fe6 = %s sec" % (time.time() - t1))

# Bin(13) w/ 5 bins, RC(12), FH(14) --> Total: 51.2s, NB: 40.6s
t1 = time.time()
nb_time = applyFTset5(criteo, 5, nb_time)
ft_time = ft_time + ((time.time() - t1) * 1000) #millisec
print("Elapsed time for fe5 = %s sec" % (time.time() - t1))

timers[:3] = ft_time - nb_time
timers[3:] = nb_time
resfile = "featureeng_spark.dat"
np.savetxt(resfile, timers, delimiter="\t", fmt='%f')
print(timers)

