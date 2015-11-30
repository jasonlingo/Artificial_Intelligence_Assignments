import numpy as np
import operator
import math
from classifier import Classifier

class DecisionTree(Classifier):
    """
    A decision tree classifier.
    """
    def __init__(self, igMode, training_data, attributes, parentExample, attrValue):
        self.igMode = igMode
        self.example = training_data  # training example
        self.attributes = attributes
        self.parentEx = parentExample
        self.attrValue = attrValue

        self.subtree = {}
        self.attrIdx = None

    def train(self):
        if self.example == []:
            return self.pluralityValue(self.parentEx)
        elif self.hasSameLabel(self.example):
            return self.example[0][0]
        elif self.attributes == []:
            return self.pluralityValue(self.example)
        else:
            self.attrIdx = self.argmaxAIG(self.example)

            # for v in self.valueOfA(a, self.example):
            for v in self.attrValue[self.attrIdx]:
            # for v in [0.0, 1.0, 2.0]:
                exs = [e for e in self.example if e[self.attrIdx] == v]
                newAttr = self.attributes[:]
                newAttr.remove(self.attrIdx)
                newTree = DecisionTree(self.igMode, exs, newAttr, self.example, self.attrValue).train()
                self.subtree[v] = newTree

            return self

    def predict(self, data):
        if data[self.attrIdx] not in self.subtree:  # FIXME
            return self.pluralityValue(self.parentEx)

        if isinstance(self.subtree[data[self.attrIdx]], DecisionTree): # use round() because some 0.6 will be 0.59999999999999998
            return self.subtree[data[self.attrIdx]].predict(data)
        else:
            return self.subtree[data[self.attrIdx]]

    def test(self, test_data):
        pass

    def pluralityValue(self, ex):
        """
        Find the most common label of the given examples
        Args:
            ex: the given examples
        Returns:
            the most common label
        """
        labelCount = self.countLabels(ex)
        if labelCount is None:
            return 0  # FIXME
        return max(labelCount.iteritems(), key=operator.itemgetter(1))[0]

    def valueOfA(self, a, ex):
        """
        Find the distinct values of attribute a among only the given examples
        (not all example from the beginning).

        Args:
            a: the attribute index
            ex: the given example
        Returns:
            a list of distinct attribute values
        """
        value = set()
        for e in ex:
            value.add(e[a])
        return list(value)

    def argmaxAIG(self, ex):
        """
        Find the attribute with maximum information gain.

        Args:
            ex: the given examples
        Returns:
            the attribute index that has the maximum information gain.
        """
        maxAIdx = None
        maxAGain = -1
        for a in self.attributes:
            ig = self.informationGain(a, ex)
            if self.igMode == "igr" and ig != 0:
                ig /= self.intrinsicValue(a, self.example)  # TODO: check formulation
            if ig > maxAGain:
                maxAIdx = a
                maxAGain = ig
        return maxAIdx

    def informationGain(self, a, ex):
        entropy = self.entropy(ex)

        # divide the examples into different groups by the attribute's values
        groups = {}
        for e in ex:
            if e[a] in groups:
                groups[e[a]].append(e)
            else:
                groups[e[a]] = [e]

        remainder = 0.0
        for g in groups.values():
            remainder += (len(g) / float(len(ex))) * self.entropy(g)

        return entropy - remainder

    def entropy(self, ex):
        labelCount = self.countLabels(ex)
        totalLabelNum = sum(labelCount.values())
        entropy = 0.0
        for count in labelCount.values():
            entropy += -(count / float(totalLabelNum)) * math.log((count / float(totalLabelNum)), 2)
        return entropy

    def countLabels(self, ex):
        if ex is None:
            return None

        labelCount = {}
        for e in ex:
            if e[0] in labelCount:
                labelCount[e[0]] += 1
            else:
                labelCount[e[0]] = 1
        return labelCount

    def intrinsicValue(self, a, ex):
        """
        Find the intrinsic value of given examples regarding the attribute. We first divide
        the examples into different groups by their a-th attribute values. Then calculate the
        intrinsic value by calculating the group size over the total example size multiplied
        by log_2 (the same ratio).
                                                p = |x \in ex | value(x, a) = v|             p
        Intrinsic Value = sum_{v \in value(a)} ---------------------------------- * log_2 --------
                                                              |ex|                          |ex|
        Args:
            ex: the given examples
            a: the attribute index
        Return:
            The intrinsic value.
        """
        values = self.valueOfA(a, ex)
        iv = 0.0
        for v in values:
        # for v in self.attrValue[a]:  # TODO: check which values we should use
            p = len([e for e in ex if e[a] == v]) / float(len(ex))
            if p == 0:
                print p
            iv += -p * math.log(p, 2)
        return iv

    def hasSameLabel(self, ex):
        """
        Check whether all the examples have the same label

        Args:
            ex: the given examples
        Return:
            True if all the examples have the same label; otherwise return False.
        """
        labels = [e[0] for e in ex]
        return len(set(labels)) == 1