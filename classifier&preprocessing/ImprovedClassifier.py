from __future__ import division, print_function, absolute_import

import tensorflow as tf
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_1d, global_max_pool
from tflearn.layers.merge_ops import merge
from tflearn.layers.estimator import regression
from tflearn.helpers.evaluator import Evaluator
import numpy as np
from tflearn import data_utils
import _pickle
import preprocessingTest

class TweetClassifier:

  def __init__(self):
    self.pre=preprocessingTest.ProcessInput()
    #load in data
    with open('processedInput.pkl' , 'rb') as f:
      raw_data= _pickle.load(f)

    self.labels, self.text=raw_data[0],raw_data[1]

    np.random.seed(1)
    p = np.random.permutation(np.arange(len(self.labels)))
    self.labels, self.text = self.labels[p], self.text[p]
    print("labels: {0}\ttext: {1}".format(len(self.labels),len(self.text))) 

    self.vp=data_utils.VocabularyProcessor.restore('vocab.txt')

  def buildNet(self):
    #necessary to allow the model to be loaded after it has been trained
    tf.reset_default_graph()

    #build input layer to accept 140 chars
    network = input_data(shape=[None, 72], name='input')
    #embedded layer
    network = tflearn.embedding(network, input_dim=len(self.vp.vocabulary_)+2, output_dim=128)

    #create three convolutional layers
    branch1 = conv_1d(network, 128, 3, padding='valid', activation='relu', regularizer="L2")
    branch2 = conv_1d(network, 128, 4, padding='valid', activation='relu', regularizer="L2")
    branch3 = conv_1d(network, 128, 5, padding='valid', activation='relu', regularizer="L2")

    #merge all incoming tensors into a single tenso
    network = merge([branch1, branch2, branch3], mode='concat', axis=1)

    #expand dimensions of network to 3d tensor, as input is a 1d tensor
    network = tf.expand_dims(network, 2)
    #perform reduction operation over input tensor
    network = global_max_pool(network)

    #prevent overfitting by including dropout
    network = dropout(network, 0.8)

    #output layer
    network = fully_connected(network, 8, activation='softmax')
    network = regression(network, optimizer='adam', learning_rate=0.0001,
    loss='categorical_crossentropy', name='target')

    return network

  def train(self,network):
    model = tflearn.DNN(network,
      tensorboard_verbose=0,tensorboard_dir='tflearn_logs/',
      checkpoint_path='checkpoints/ImprovedModel.tfl.ckpt',
      best_checkpoint_path='bestCheckpoints/ImprovedModel.tfl.ckpt')
    
    tf.summary.FileWriter('/tflearn_logs', graph=tf.get_default_graph())
    model.fit(self.text,self.labels,validation_set=0.15,batch_size=256,
      n_epoch=100,show_metric=True)

    model.save('ImprovedModel.tfl')

  '''
  def loadModel(self):
    #model = Evaluator(buildNet())
    model = tflearn.DNN(self.buildNet())
    model.load('./ImprovedModel.tfl',weights_only=False)
    labelIndices = ["london\t","birmingham","manchester","glasgow","newcastle","sheffield","los angeles","new york"]
    while True:
      tweet=input('\nType in a tweet:\n')
      if(tweet=='qq'):
        break
      tweet=self.pre.singleInput(tweet)
      labels=np.asarray(np.multiply(model.predict(tweet),100),dtype=np.int32)
      for i in range(0,labels.size):
        print("{0}:\t\t\t%{1}".format(labelIndices[i],labels[0][i]))
  '''
        
  def loadModel(self):
    self.model = tflearn.DNN(self.buildNet())
    self.model.load('./ImprovedModel.tfl',weights_only=False)

  def predict(self, tweet):
    tweet = self.pre.singleInput(tweet)
    return np.asarray(np.multiply(self.model.predict(tweet),100),dtype=np.float32)

def main():
  tc=TweetClassifier()
  tc.train(tc.buildNet())

if __name__ == "__main__":
  main()
