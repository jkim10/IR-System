import sys
import csv

if __name__ == "__main__":
    if(len(sys.argv) < 4):
        print(f"Usage: {sys.argv[0]} <integrated_dataset> <min_sup> <min_conf>")
        quit()
    data = []
    file = csv.reader(sys.argv[1])
    for row in file:
        data.append(row)
    min_sup = sys.argv[2]
    min_conf = sys.argv[3]
    # Algorithm


    out = open("output.txt","w")
    out.write(f"==Frequent Itemsets (min_sup={min_sup})\n")
    # Print Frequent Itemsets
    out.write(f"==High-confidence association rules (min_conf={min_conf})\n")
    # Print High Confidence association rules