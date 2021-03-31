import sys
import csv
from collections import defaultdict

if __name__ == "__main__":
    if(len(sys.argv) < 4):
        print(f"Usage: {sys.argv[0]} <integrated_dataset> <min_sup> <min_conf>")
        quit()
    with open(sys.argv[1]) as f:
        rows = csv.reader(f)
        data = list(rows)
        data = data[1:]
    min_sup = sys.argv[2]
    min_conf = sys.argv[3]
    candidate = set()
    L = defaultdict(int)

    # Apriori Algorithm
    for row in data:
        for x in row:
            L[x] +=1 
    import code; code.interact(local=dict(globals(), **locals()))



    
    # Uncomment when we ready to output
    # out = open("output.txt","w")
    # out.write(f"==Frequent Itemsets (min_sup={min_sup})\n")
    # # Print Frequent Itemsets

    # out.write(f"==High-confidence association rules (min_conf={min_conf})\n")
    # # Print High Confidence association rules