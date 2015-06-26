'''
author: Jonny

Generate random data.
'''

import numpy as np

def genData(N,D):
    with open('data','w') as f:
        for n in range(N):
            y = 1 if np.random.rand()>0.5 else -1 
	    li = str(y)+','
            x = np.random.randn(1,D)
            li += ','.join(str(i) for i in x[0]) 
	    li = li + '\n'
            f.write(li)


if __name__ == "__main__":
    genData(1000,20)

