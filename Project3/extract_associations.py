import sys
import csv
from collections import defaultdict

# Going to find all subsets of L_k ustin L_k-1
def combinations(L,k):
    candidates = set()
    if(k==2):
        L_k = list(L)
    else:
        L_k = [x for x in L if len(x) == (k-1)]

    for e in L_k:
        for n in L_k:
            temp = set()
            temp.add(e)
            temp.add(n)
            if(len(temp) == k):
                candidates.add(tuple(temp))
    return candidates

def subset(C_k, row):
    out = set()
    for candidate in C_k:
        if(set(candidate).issubset(row)):
            out.add(candidate)
    return out

if __name__ == "__main__":
    if(len(sys.argv) < 4):
        print(f"Usage: {sys.argv[0]} <integrated_dataset> <min_sup> <min_conf>")
        quit()
    with open(sys.argv[1]) as f:
        rows = csv.reader(f)
        data = list(rows)
        data = data[1:]

    # Comment this out to use real data    
    data = [
            ["pen","ink","diary","soap"],
            ["pen","ink","diary"],
            ['pen',"diary"],
            ['pen',"ink","soap"]
           ]
    min_sup = float(sys.argv[2])
    min_conf = float(sys.argv[3])
    candidate = set()
    L = defaultdict(int)
    num_rows = len(data)
    num_columns = len(data[0])

    # TODO: Apriori Algorithm
    # Calculate L1 Itemsets (line 1 of algorithm)
    for row in data:
        for x in row:
            if(x != ''):
                L[(x)] +=1
    for key in list(L.keys()): # Filter out keys not above min_sup
        s = L[key] / num_rows
        if(s < min_sup):
            del L[key]

    for k in range(2,num_columns): # (line 2 of algorithm)
        C_k = combinations(L,k) # (line 3 of algorithm)
        added_candidates = set()
        for row in data: # (line 4 of algorithm)
            C_t = subset(C_k,row)
            for candidate in C_t:
                L[candidate] += 1
                added_candidates.add(candidate)
        for key in added_candidates: # Filter out keys not above min_sup
            s = L[key] / num_rows
            if(s < min_sup):
                del L[key]



    
    # Uncomment when we ready to output
    # out = open("output.txt","w")
    # out.write(f"==Frequent Itemsets (min_sup={min_sup})\n")
    # # TODO: Print Frequent Itemsets
    for freq in L.keys():
        print(f"[{freq}], {L[freq] / num_rows}")

    # out.write(f"==High-confidence association rules (min_conf={min_conf})\n")
    # # TODO: Print High Confidence association rules