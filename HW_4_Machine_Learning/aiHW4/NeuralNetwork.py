from classifier import Classifier
import numpy as np
import math
from collections import Counter


class NeuralNetwork(Classifier):
    """
    A neural network classifier.
    """

    def __init__(self, training_data, nodeNum, weightInitMode=None):
        # number of total training iteration
        self.ITERATION = 10000

        # for randomly initializing theta
        self.EPISLON = 0.12

        # learning rate
        self.ALPHA = 0.03

        # decay rate for momentum
        self.momentum_factor = 0.5

        # dictionary for momentum
        self.momentum = {}

        # number of classes for the classification
        self.classNum = nodeNum[-1]

        # number of nodes in each layers
        self.nodeNum = {}
        i = 1
        for nn in nodeNum:
            self.nodeNum[i] = nn
            i += 1

        # number of total layers including the input and output layers
        self.layerNum = len(nodeNum)

        # the weight (theta) initialization mode
        self.weightInitMode = weightInitMode

        self.theta = {}
        # self.layers = {}
        self.delta = {}
        self.z = {}
        self.a = {}
        self.djdw = {}

        # get labels and nodes for the first layer (input layer)
        self.labels, self.x = self.prepareForTraining(training_data)
        # self.a[1] = self.x

    def prepareForTraining(self, training_data):
        """
        Split the labels and features from the input training_data.
        Args:
            training_data:
        Returns:
            labels: a (exampleNum x classNum) matrix that contains label for each training example
            examples: a (exampleNum x featureNum ) matrix for the input training example
        """
        labels = training_data.copy()[:, 0]          # get the first column (label) from the matrix
        labels = labels.reshape(labels.shape[0], 1).T

        # FIXME: move to feedforward
        examples = training_data.copy()[:, 1:]       # get the rest columns (features of examples) from the matrix
        onesCol = np.ones((examples.shape[0], 1))
        examples = np.hstack((examples, onesCol))    # add one column (all ones) for bias
        return labels, examples

    def train(self):
        """
        Train this neural network with feed-forward and back-propagation.
        When training is finished, the theta can be used for prediction.
        Args:
            training_data: a matrix (numpy format).
        """
        print ("Start training neural network...")

        self.initTheta()

        training = True
        iter = 0
        # for iter in range(self.ITERATION):
        while training and iter <= self.ITERATION:
            iter += 1
            yHat = self.feedForward(self.x)
            cost, costMat = self.cost(self.labels, yHat)
            if cost < 0.01:
                training = False

            if iter % 1000 == 0:
                print "cost = ", cost, " (", iter, " iteration)"
                # print costMat

            self.backpropagation()
            self.updateTheta()

            if iter % 500000 == 0:
                decision = raw_input("Continue training? (Y/N)")
                if decision.lower() == "n":
                    training = False

        print ("cost = ", cost)

    def initTheta(self):
        """
        initialize each theta by
        theta = random matrix * 2 epislon - epislon
        so each element will be in the range [-epislon, epislon]
        Returns:

        """
        # print "Initialize theta"
        initW = {}
        for i in range(1, self.layerNum):
            if self.weightInitMode is None:
                # Use the default value EPISLON
                # the initial value of theta will be within [-EPISLON, EPISLON]
                initW[i] = self.EPISLON
            elif self.weightInitMode == "shallow":
                # Use number of node in previous layer (n)
                # w = 1 / math.sqrt(n)
                # the initial value of theta will be within [-w, w]
                initW[i] = 1 / float(math.sqrt(self.nodeNum[i]))
            elif self.weightInitMode == "deep":
                # Use the number of nodes in previous and next layers
                # w = math.sqrt(6) / (math.sqrt(preNode + nextNode))
                # the initial value of theta will be within [-w, w]
                initW[i] = math.sqrt(6) / math.sqrt(self.nodeNum[i] + self.nodeNum[i+1])

        for i in range(1, self.layerNum):  # layer number starts from 1,  add one bias
            # th = np.random.rand(self.nodeNum[i+1], self.nodeNum[i] + 1) * 2 * initW[i] - initW[i]

            # theta[previous layer, next layer]
            th = np.random.rand(self.nodeNum[i] + 1, self.nodeNum[i+1]) * 2 * initW[i] - initW[i]
            self.theta[i] = th

    def feedForward(self, x):
        """
        Compute all the x in each layer except the first input layer.
        """
        # print "feedforward"
        self.a[1] = x.T  # transform the example to a column-based matrix

        for i in range(1, self.layerNum):
            # print i, "th layer"
            # self.z[i + 1] = self.a[i].dot(self.theta[i].T)                # z_{i+1} = a_i * theta_i
            # self.a[i + 1] = sigmoid(self.z[i + 1])                        # a_{i+1} = sigmoid(z_{i+1})

            # print self.theta[i].T.shape
            # print self.a[i].shape

            self.z[i+1] = np.dot(self.theta[i].T, self.a[i])
            self.a[i+1] = sigmoid(self.z[i+1])

            # add bias column to each layer except the output layer
            if i + 1 < self.layerNum:
                # onesCol = np.ones((self.a[i + 1].shape[0], 1))
                # self.a[i + 1] = np.hstack((self.a[i + 1], onesCol))
                # print "add row"
                # print self.a[i+1].shape
                conesRow = np.ones((1, self.a[i+1].shape[1]))
                self.a[i+1] = np.vstack((self.a[i+1], conesRow))
                # print self.a[i+1].shape
        return self.a[self.layerNum]


    def backpropagation(self):
        """
        Compute all the delta for each layer except the first input layer.
        """
        # print "backpropagation"

        # compute the delta for the output layer delta = (y - a) .* a .* (1 - a)
        self.delta[self.layerNum] = -(self.labels - self.a[self.layerNum]) * sigmoidDe(self.z[self.layerNum])

        # compute the delta for other layers (from layerNum - 1 to 1)
        # no delta for input layer
        for l in range(self.layerNum - 1, 1, -1):
            # print l, "-th layer -------------------------"
            # print self.a[l].shape
            # print self.theta[l].shape
            # if l + 1 != self.layerNum:
            #     print self.delta[l+1][:,:-1].shape
            # else:
            #     print self.delta[l+1].shape
            # print "-------------------------------------"

            if l + 1 != self.layerNum:
                preDelta = self.delta[l+1]#[:-1, :]  # ignore the bias
            else:
                preDelta = self.delta[l+1]
            self.djdw[l] = np.dot(self.a[l], preDelta.T)
            # print l, " ----------"
            # print self.theta[l][:-1, :].shape
            # print preDelta.shape
            # print sigmoidDe(self.z[l]).shape
            self.delta[l] = np.dot(self.theta[l][:-1, :], preDelta) * sigmoidDe(self.z[l])
        self.djdw[1] = np.dot(self.a[1], self.delta[2].T)
        # print "didw shape:"
        # for i in range(1, self.layerNum):
        #     print self.djdw[i].shape
        # return

    def updateTheta(self):
        """
        Update every theta in network using deltas.
        for each layer of theta:
            theta_ij = theta_ij + self.ALPHA * a_i * delta_j
        """

        for l in range(1, self.layerNum):
            self.theta[l] -= self.ALPHA * self.djdw[l]
        # # print "udpate theta"
        # for l in range(self.layerNum - 1, 0, -1):
        #     # print self.theta[l].shape
        #     if l + 1 < self.layerNum:
        #         preDelta = self.delta[l+1][:, :-1].T
        #     else:
        #         preDelta = self.delta[l+1].T
        #     # print preDelta.shape
        #     # print self.a[l].shape
        #
        #     thisMomentum = self.ALPHA * (preDelta.dot(self.a[l]))
        #     if l in self.momentum:
        #         lastMomentum = self.momentum[l]
        #     else:
        #         lastMomentum = 0
        #     self.theta[l] += thisMomentum + self.momentum_factor * lastMomentum
        #     self.momentum[l] = thisMomentum

    def cost(self, labels, yHat):
        costMat = labels - yHat
        cost = sum(sum(costMat * costMat)) / 2.0
        # print "cost = ", cost
        return cost, costMat

    def predict(self, data):
        # print "predict"
        # print data.shape
        data = data.reshape(1, data.shape[0])
        # print data.shape
        # data = data.reshape(1, data.shape[0]).T
        # print "the dimension of input data is ", data.shape
        # for l in range(1, self.layerNum):
        #     # print l, "-th layer"
        #     # print data.shape
        #     # print transpose(self.theta[l]).shape
        #     data = data.dot(self.theta[l].T)
        #     data = sigmoid(data)
        #     if l + 1 < self.layerNum:
        #         onesCol = np.ones((data.shape[0], 1))
        #         data = np.hstack((data, onesCol))
        yHat = self.feedForward(data)

        if self.classNum > 2:
            maxV = -1
            maxIdx = None
            i = 0
            for d in data:
                if d > maxV:
                    maxV = d
                    maxIdx = i
                i += 1
            return maxIdx
        else:
            if yHat.max() >= 0.5:
                print yHat, " -> ", 1
                return 1
            else:
                print yHat, " -> ", 0
                return 0

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoidDe(z):
    return sigmoid(z) * (1 - sigmoid(z))