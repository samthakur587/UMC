# Redefining the UMCFunction class with the provided code
import math
from collections import defaultdict
import numpy as np
from collections import Counter
from bin import Bin
from constents import Constants
from key import Key
from sortedobject import SortedObject
class UMCFunction():
    def __init__(self):
        pass

    def computeCE_vals_array(self,vals, hasSorted=True):
        if len(vals) <= 1:
            return 0
        
        if not hasSorted:
            vals.sort()
        
        num_items = len(vals)
        ce = 0
        logBase = math.log(Constants.LOG_BASE)
        
        for i in range(num_items - 1):
            if vals[i + 1] < vals[i]:
                raise ArithmeticError(f"non-decreasing order is violated: vals[i] = {vals[i]}, vals[i + 1] = {vals[i + 1]}")
            
            if vals[i + 1] != vals[i]:
                ce += (vals[i + 1] - vals[i]) * ((i + 1) / num_items) * math.log((i + 1) / num_items) / logBase
        
        return -ce
    
    
    def formInitialBins(self, data, rank, colOrder, X, numDesiredBins):
        r = len(data)
        ret = []
        actualCol = colOrder[X]

        # Extract distinct values
        distinctValues = defaultdict(list)
        sortedKeys = []
        for i in range(r):
            k = data[rank[i][0]][actualCol]
            if k not in distinctValues:
                sortedKeys.append(k)  # distinct values
            distinctValues[k].append(rank[i][0])

        sortedKeys.sort()

        # Number of distinct values per bin
        numRows = r
        totalNumBins = numDesiredBins
        desiredBinSize = numRows // totalNumBins

        # Discretize
        indices = [0] * len(distinctValues)
        i = 1
        curDistinctVal = 0
        curBinIndex = 1
        while curDistinctVal < len(indices):
            count = sum(len(distinctValues[sortedKeys[j]]) for j in range(len(indices)) if indices[j] == curBinIndex)
        
            if count and abs(count + len(distinctValues[sortedKeys[curDistinctVal]]) - desiredBinSize) >= abs(count - desiredBinSize):
                curBinIndex += 1
                desiredBinSize = (numRows - i + 1) // (totalNumBins - curBinIndex + 1)
            indices[curDistinctVal] = curBinIndex
            i += len(distinctValues[sortedKeys[curDistinctVal]])
            curDistinctVal += 1

        # Create bin
        curBinIndex = 1
        curDistinctVal = 0
        while curDistinctVal < len(indices):
            ds = []
            while curDistinctVal < len(indices) and indices[curDistinctVal] == curBinIndex:
                ds.extend(distinctValues[sortedKeys[curDistinctVal]])
                curDistinctVal += 1
        
            tmpBin = Bin(ds)
            ret.append(tmpBin)
            curBinIndex += 1

        # Control check
        count = sum(len(bin.getPoints()) for bin in ret)
        if count != numRows:
            raise ArithmeticError("some point is missing!")

        return ret  # return a bin-like list according to the distinct values to split bins


    def generateRank(self,data):
        r = len(data)
        c = len(data[0])
        rank = [[0] * c for _ in range(r)]

        # Sort data per dimension
        for j in range(c):
            sos = sorted([(data[i][j], i) for i in range(r)])
            for i in range(r):
                rank[i][j] = sos[i][1]

        return rank

    def rankColumns(self,ces):
        c = len(ces)
        # Create list of tuples containing the value and its index
        sos = sorted([(value, idx) for idx, value in enumerate(ces)], reverse=True)
    
        # Extract indices based on the sorted order
        order = [item[1] for item in sos]
    
        return order

    
    def createHypercubes(self,discrete, rank, colOrder, X, Y, beta, count):
        map_ = [None] * beta
        r = len(discrete)
        c = 0

        for i in range(r):
            actualID = rank[i][colOrder[Y]]

            # Cube of already discretized dimensions
            vals = [discrete[actualID][colOrder[j]] for j in range(X)]

            # Bin of X
            idx = discrete[actualID][colOrder[X]]

            # Create dict if it's not there yet
            if not map_[idx]:
                map_[idx] = {}

            # Retrieve point ids
            key = tuple(vals)  # Using tuple as a key 
            if key in map_[idx]:
                pids = map_[idx][key]
            else:
                pids = []
            pids.append(actualID)

            # Add list of ids to dict
            map_[idx][key] = pids
            count[idx] += 1  # the size of bin of X
            c += 1

        if c != r:
            raise ArithmeticError("Some records are missing!")

        return map_

    def extractValues(self,data, actualCol, map_, k):
        pids = map_.get(k, [])
        return [data[id][actualCol] for id in pids]
    
    def merge(self,a, b):
        ret = []
        idxA, idxB = 0, 0
        sizeA, sizeB = len(a), len(b)
    
        while idxA < sizeA and idxB < sizeB:
            if a[idxA] < b[idxB]:
                ret.append(a[idxA])
                idxA += 1
            else:
                ret.append(b[idxB])
                idxB += 1

        if idxA >= sizeA:
            ret.extend(b[idxB:])
        else:
            ret.extend(a[idxA:])
    
        return ret
    
    def computeF(self, data, discrete, rank, colOrder, X, Y, beta):
        actualCol = colOrder[Y]
    
        # create hypercubes
        count = [0] * beta
        map_ = self.createHypercubes(discrete, rank, colOrder, X, Y, beta, count)
    
        # pre-computation for f[i][i]
        f = [[0 for _ in range(beta)] for _ in range(beta)]
        for i in range(beta):
            values = map_[i].values()
            for pids in values:
                v = [data[id][actualCol] for id in pids]
                ce = self.computeCE_vals_array(v, True)
                f[i][i] += len(v) * ce / count[i]

            if f[i][i] < 0 and abs(f[i][i]) > Constants.MAX_ERROR:
                raise ArithmeticError(f"Wrong score f[i][i] = {f[i][i]}")
    
        # pre-computation for f[j][i]
        for j in range(beta):
            # initialize the hash
            tmpMap = {}
            keys = map_[j].keys()
            for k in keys:
                d = self.extractValues(data, actualCol, map_[j], k)
                tmpMap[k] = d

            # populate hash incrementally
            c = count[j]
            for i in range(j + 1, beta):
                c += count[i]
                keys = map_[i].keys()
                for k in keys:
                    d = self.extractValues(data, actualCol, map_[i], k)
                    cur = tmpMap.get(k)
                    if cur is None: # key is not there
                        cur = d
                    else:
                        cur = self.merge(cur, d)
                    tmpMap[k] = cur
            
                values = tmpMap.values()
                for val in values:
                    ce = self.computeCE_vals_array(val, True)
                    f[j][i] += len(val) * ce / c

                if f[j][i] < 0 and abs(f[j][i]) > Constants.MAX_ERROR:
                    raise ArithmeticError(f"Wrong score f[j][i] = {f[j][i]}")
    
        return f

    def IQR(self, data, colOrder, Y):
        r = len(data)
        col = [data[i][colOrder[Y]] for i in range(r)]
        col.sort()
        pos1 = int(r * 0.75)
        pos2 = int(r * 0.25)
        return abs(col[pos1] - col[pos2])
    
    def _computeScore(self, data, discrete, rank, ces, colOrder, X, Y, numpoints):
        r = len(data)
        numDesiredBins = int(r // r**numpoints)
        a = self.formInitialBins(data, rank, colOrder, X, numDesiredBins)
        beta = len(a)
        actualCol = colOrder[X]

        s = [0] * beta
        sum_val = 0
        for i in range(beta):
            pids = a[i].getPoints()
            sum_val += len(pids)
            s[i] = sum_val

            for id in pids:
                discrete[id][actualCol] = i

        f = self.computeF(data, discrete, rank, colOrder, X, Y, beta)

        val = [float('inf')] * beta
        b = [None] * beta
        val[0] = f[0][0]
        b[0] = [a[0]]
        for i in range(1, beta):
            pos = -1
            for j in range(i):
                t = (s[i] - s[j]) * f[j + 1][i] / s[i] + s[j] * val[j] / s[i]
                if t < val[i]:
                    val[i] = t
                    pos = j

            if f[0][i] < val[i]:
                val[i] = f[0][i]
                pos = -1

            b[i] = []
            if pos != -1:
                b[i].extend(b[pos])

            pids = []
            for k in range(pos + 1, i + 1):
                pids.extend(a[k].getPoints())
            tmp = Bin(pids)
            b[i].append(tmp)

        finalBins = b[beta - 1]
        c = 0
        binsize = [0] * len(finalBins)
        for bin in finalBins:
            pids = bin.getPoints()
            binsize[c] = len(pids)
            for id in pids:
                discrete[id][actualCol] = c
            c += 1

        sum2 = 0.0
        iqr = self.IQR(data, colOrder, Y)
        
        for size in binsize:
            sum2 += size * iqr * (-0.165 / size + (size - 1) * math.log(size) / (2 * math.log(Constants.LOG_BASE))) / (1.8 * (size + 1))

        expectedvalue = 0.0
        if Y >= 2:
            expectedvalue = ces[colOrder[Y]]
        else:
            expectedvalue = ces[colOrder[Y]] - sum2 / r

        return [ces[colOrder[Y]] - val[beta - 1], math.log(len(b[beta - 1])) / math.log(Constants.LOG_BASE), val[beta - 1], expectedvalue]

    def computeScore(self, data, preRank=None):
        r, c = len(data), len(data[0])

        rank = preRank
        if rank is None:
            rank = self.generateRank(data)
    
        discrete = [[-1 for j in range(c)] for i in range(r)]

        # compute ces
        ces = []
        for j in range(c):
            a = [data[rank[i][j]][j] for i in range(r)]
            ces.append(self.computeCE_vals_array(a, True))

        # rank columns
        colOrder = self.rankColumns(ces)

        # compute score
        sumCES = 0
        sumScore = 0
        sumLog = 0
        cce = [0 for _ in range(c - 1)]
        min_val = 0

        for j in range(1, c):
            ret = self._computeScore(data, discrete, rank, ces, colOrder, j - 1, j, Constants.epsilon)
            sumScore += ret[0] - ret[3]
            sumLog += ret[1]
            sumCES += ces[colOrder[j]] - ret[3]
            cce[j - 1] = ret[2]

        min_val = min(cce)

        t = sumScore / (sumCES - (c - 1) * min_val)

        return t

# testing the t value

if __name__ == "__main__":
    umc_instance = UMCFunction()
    # Testing on a random 1000x10 matrix
    random_data = np.random.rand(1000, 8)
    t_1000x10 = umc_instance.computeScore(data=random_data, preRank=None)
    print(t_1000x10)
