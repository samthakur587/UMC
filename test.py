import math
import numpy as np
from collections import defaultdict

def formInitialBinsDict(data, rank, colOrder, X, numDesiredBins):
    r = len(data)
    bins_dict = {}
    actualCol = colOrder[X]
    
    # Extract distinct values
    distinctValues = defaultdict(list)
    sortedKeys = []
    for i in range(r):
        k = data[rank[i][actualCol]][actualCol]
        if k not in distinctValues:
            sortedKeys.append(k)  # distinct values
        distinctValues[k].append(rank[i][actualCol])
    
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
    
    # Create bin dictionary
    curBinIndex = 1
    curDistinctVal = 0
    while curDistinctVal < len(indices):
        for i in range(curDistinctVal + 1, len(indices)):
            if indices[i] != curBinIndex:
                break
        newDistinctVal = i
        
        # Get current value and add the corresponding points to the bin
        ds = []
        for i in range(curDistinctVal, newDistinctVal):
            ds.extend(distinctValues[sortedKeys[i]])
        
        # Define the range for the bin
        bin_range = (sortedKeys[curDistinctVal], sortedKeys[newDistinctVal-1])
        bins_dict[bin_range] = ds
        
        curDistinctVal = newDistinctVal
        curBinIndex += 1
    
    # Control check
    count = sum(len(bin_data) for bin_data in bins_dict.values())
    if count != numRows:
        raise ArithmeticError("some point is missing!")
    
    return bins_dict  # return a dictionary with ranges as keys and corresponding data points as values

# Sample test for the function (due to lack of context, this is a basic test)
data = [
    [2, 4],
    [3, 5],
    [2, 6],
    [4, 7],
    [5, 8],
]
rank = [(0, 1), (1, 0), (2, 2), (3, 3), (4, 4)]
colOrder = [1, 0]
X = 1
numDesiredBins = 2

formInitialBinsDict(data, rank, colOrder, X, numDesiredBins)
