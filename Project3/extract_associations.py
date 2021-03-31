import sys
import csv
from collections import defaultdict
import itertools
def combinations(L,k):
    L_k = [x for x in L if len(x) == k-1]
    return set(itertools.combinations(L, k))
if __name__ == "__main__":
    if(len(sys.argv) < 4):
        print(f"Usage: {sys.argv[0]} <integrated_dataset> <min_sup> <min_conf>")
        quit()
    with open(sys.argv[1]) as f:
        rows = csv.reader(f)
        data = list(rows)
        data = data[1:]
    min_sup = float(sys.argv[2])
    min_conf = float(sys.argv[3])
    candidate = set()
    L = defaultdict(int)
    num_rows = len(data)

    # TODO: Apriori Algorithm
    # Calculate L1 Itemsets (line 1 of algorithm)
    for row in data:
        for x in row:
            if(x != ''):
                L[x] +=1
    for key in list(L.keys()): # Filter out keys not above min_sup
        s = L[key] / num_rows
        if(s < min_sup):
            del L[key]

    
    # Start Line 2 of Algorithm 
    import code; code.interact(local=dict(globals(), **locals()))



    
    # Uncomment when we ready to output
    # out = open("output.txt","w")
    # out.write(f"==Frequent Itemsets (min_sup={min_sup})\n")
    # # TODO: Print Frequent Itemsets

    # out.write(f"==High-confidence association rules (min_conf={min_conf})\n")
    # # TODO: Print High Confidence association rules