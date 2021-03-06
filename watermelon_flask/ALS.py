import pickle
import numpy as np
import pandas as pd 
from collections import defaultdict

class PreCalculated():
    def __init__(self, path):
        self.preItem = None
        self.preScore = None
        self.songIdx = {}
        self.songSets = {}
        self.rankScore = [0.02 *i for i in range(50,0,-1)]

        
        if path:
            self.preItem = self.loadData(path + "ALS_pre_rec_item.bin")
            self.preScore = self.loadData(path + "ALS_pre_rec_score.bin")
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
            ret[i] = (ret[i] - mi) / (mx - mi)
        return ret

    def getRecommendation(self, songs=[], nSimilar=3):
        cos = self.getCosSimilar([int(song) for song in songs], self.songIdx, self.songSets)
        rec = []
        for i in cos.argsort()[-nSimilar:]:                
            # simliarity = cos[i]
            # ALS user-i-th의 추천 = self.preRec[i]]

            scaledScore = self.minmaxScale(self.preScore[i])
            scaledScore *= cos[i]

            rec.append(list(zip(self.preItem[i], scaledScore)))
        
        result = self.combMNZ(rec)
        ret = []
        for item in result:
            mid, score = item
            mid = str(int(mid))
            if mid in songs:
                continue
            ret.append((mid, score))

        return ret
