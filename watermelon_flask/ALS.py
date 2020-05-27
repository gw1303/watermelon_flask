import pickle
import numpy as np
import pandas as pd 
from collections import defaultdict

class PreCalculated():
    def __init__(self, path):
        self.preRec = None
        self.songIdx = {}
        self.songSets = {}
        self.playList = None
        
        if path:
            self.preRec = self.loadData(path + "ALS_pre_recommendations.bin")
            self.songIdx = self.loadData(path + "songIdx.bin")
            self.songSets = self.loadData(path + "songSets.bin")        
            self.playList = pd.read_pickle(path + 'playLists.bin')

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

    def combMNZ(self, ranks):
        # ranks = [[(musicId, prob), ...], ...]
        nonZero = defaultdict(int)
        combSUM = defaultdict(float)
        ids = set()
        for i in range(len(ranks)):
            for j in range(len(ranks[i])):
                mid, score = ranks[i][j]
                nonZero[mid] += 1 if score>0 else 0
                combSUM[mid] += score
                ids.add(mid)
        
        rankResult = [(mid, combSUM[mid]*nonZero[mid]) for mid in ids]

        return sorted(rankResult, key=lambda x: x[1], reverse=True)
        

    def minmaxScale(self, arr):
        ret = arr[:]
        mi = 9999
        mx = 0
        for i in range(len(ret)):
            mi = ret[i] if ret[i] < mi else mi
            mx = ret[i] if ret[i] > mx else mx
        for i in range(len(ret)):
            ret[i] = (ret[i] - mi) / mx
        return ret

    def getRecommendataion(self, songs=[], nSimilar=3):
        cos = self.getCosSimilar([int(song) for song in songs], self.songIdx, self.songSets)
        rec = []
        for i in cos.argsort()[-nSimilar:]:                
            # simliarity = cos[i]
            # ALS user-i-th의 추천 = self.preRec[i]]
            ids = []
            scores = []
            for mid, score in self.preRec[i]:
                ids.append(mid)
                scores.append(score)

            scaledScore = np.array(self.minmaxScale(scores))
            scaledScore *= cos[i]

            rec.append([item for item in zip(ids, scaledScore)])
        
        return self.combMNZ(rec)     
