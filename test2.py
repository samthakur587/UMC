import numpy as np
def generateRank(data):
        r,c = data.shape
        rank = [[0] * c for _ in range(r)]
        print(rank)
        print(r,c)
        # Sort data per dimension
        for j in range(c):
            sos = sorted([(data[i][j], i) for i in range(r)])
            print(sos)
            for i in range(r):
                rank[i][j] = sos[i][1]

        return rank

