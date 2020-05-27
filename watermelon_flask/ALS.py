import pickle
import numpy as np
import pandas as pd 

class PreCalculated():
    def __init__(self, path):
        self.prePred = None
        self.songIdx = {}
        self.songSets = {}
        
        if path:
            self.prePred = self.loadData(path + "ALS_pre_recommendations.bin")
            self.songIdx = self.loadData(path + "songIdx.bin")
            self.songSets = self.loadData(path + "songSets.bin")        

    def loadData(self, path):
        with open(path, 'rb') as f:
            data = pickle.load(f) 
            return data

    def itemToIdx(self, items, typIdx):
        return set([typIdx[item] for item in items])

    def getCosSimilar(self, items, typIdx, typSets):
        res = []
        iset = self.itemToIdx(items, typIdx)
        for s in typSets:
            if len(s):
                res.append(len(iset & s)/(np.sqrt(len(s))*np.sqrt(len(iset))))
            else:
                res.append(0)
        return np.array(res)

    def combMNZ(self):
        pass

    def getRecommendataion(self, songs=[]):
        pass

    
    