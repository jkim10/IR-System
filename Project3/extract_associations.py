import sys
import csv

if __name__ == "__main__":
    if(len(sys.argv) < 4):
        print(f"Usage: {sys.argv[0]} <integrated_dataset> <min_sup> <min_conf>")
        quit()
    with open(sys.argv[1]) as f:
        data = [line.split() for line in f]
        data = data[1:]
    min_sup = sys.argv[2]
    min_conf = sys.argv[3]
    # Apriori Algorithm
    print(len(data))

    out = open("output.txt","w")
    out.write(f"==Frequent Itemsets (min_sup={min_sup})\n")
    # Print Frequent Itemsets

    out.write(f"==High-confidence association rules (min_conf={min_conf})\n")
    # Print High Confidence association rules