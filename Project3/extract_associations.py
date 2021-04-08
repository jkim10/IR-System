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
            temp = e.union(n)
            if(len(temp) == k):
                candidates.add(temp)
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
    # data = [
    #         ["pen","ink","diary","soap"],
    #         ["pen","ink","diary"],
    #         ['pen',"diary"],
    #         ['pen',"ink","soap"]
    #        ]
    min_sup = float(sys.argv[2])
    min_conf = float(sys.argv[3])
    candidate = set()
    L = defaultdict(int)
    L1 = set()
    num_rows = len(data)
    num_columns = len(data[0])

    # TODO: Apriori Algorithm
    # Calculate L1 Itemsets (line 1 of algorithm)
    for row in data:
        for x in row:
            if(x != ''):
                L[frozenset([x])] +=1
                L1.add(x)
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
                candidate = frozenset(candidate)
                L[candidate] += 1
                added_candidates.add(candidate)
        for key in added_candidates: # Filter out keys not above min_sup
            s = L[key] / num_rows
            if(s < min_sup):
                del L[key]



    
    # Uncomment when we ready to output
    # out = open("output.txt","w")
    print(f"==Frequent Itemsets (min_sup={min_sup*100}%)")
    # # TODO: Print Frequent Itemsets
    sup_print = []
    for freq in L.keys():
        support = L[freq] / num_rows
        sup_print.append((','.join(freq), support))
    sup_print = sorted(sup_print, key=lambda x: (-x[1],x[0]))
    for x in sup_print:
        print(f"[{x[0]}], {x[1]*100}%")
    print(f"==High-confidence association rules (min_conf={min_conf*100}%)")
    # # TODO: Print High Confidence association rules
    above_conf = []
    seen = set()
    for freq in L.keys():
        if(len(freq) == 1):
            continue
        for n in freq:
            right_hs = frozenset([n])
            left_hs = freq.difference(right_hs)
            if(left_hs in seen):
                continue
            else:
                seen.add(left_hs)
            confidence = L[freq] / L[left_hs]
            support = L[freq] / num_rows
            if(confidence > min_conf):
                above_conf.append((left_hs,n,confidence,support))
    above_conf = sorted(above_conf,key=lambda x: (-x[2],x[0]))
    for passed in above_conf:
        print(f"[{','.join(passed[0])}] => [{passed[1]}] (Conf: {passed[2]*100}%, Supp: {passed[3]*100}%)")