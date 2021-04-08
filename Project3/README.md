# Extract Association Rules from NYC Open Data
By Justin Kim(jyk2149) and Mavis Athene U Chen(mu2288)

## Files in Submission
- proj3.tar.gz
    - extract_associations.py
    - integrated_dataset.csv
    - output.txt
- integrated_dataset.csv
- example-run.txt
- README.md

## How to Run
```bash
    tar -zxvf proj3.tar.gz
    cd proj3
    python3 extract_associations.py integrated_dataset.csv <min_supp> <min_conf>
```


## Integrated Dataset Description
We used the [https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu](Motor Vehicle Collisions - Person) dataset from NYC Open Data, which contains details for people involved in motor vehical crashes. We want to investigate vehicle collision injuries and see if we can find any useful information about types of injury, safety equipment, etc. For example, we can see if any associations between type of injury and their role in the crash (driver, occupant, pedestrian, etc.). The dataset is very large so we sampled 2000 out of the 4.24M rows randomly. In addition, we also removed unecessary columns "Collision ID", "Crash Date", "Person ID", etc. that would not play a role in the association rules. We chose 11 out of the 21 columns as our "market basket". The columns remaining are 'PERSON_TYPE', 'PERSON_AGE', 'PERSON_INJURY', 'EJECTION', 'BODILY_INJURY', 'POSITION_IN_VEHICLE', 'SAFETY_EQUIPMENT', 'PED_LOCATION', 'PED_ACTION', 'COMPLAINT', and 'PERSON_SEX'. Finally, we categorized a person's age from 0-20, 21-50, 51-70, and 71-100 years old. 

## Internal Design of Project
We have implemented the standard apriori algorithm mentioned in 3. of Association Rule Mining Algorithm from the homework post. That is we used the algorithm from Section 2.1 of the [http://www.cs.columbia.edu/~gravano/Qual/Papers/agrawal94.pdf](Agrawal and Srikant paper in VLDB 1994), without the subset function described in section 2.1.1. We also automatically write the output to output.txt. 

## Sample Run and Result Discussions

For our sample run, we ran this instance with a minimum support of 5% and minimum confidence of 60%: `python3 extract_associations.py integrated_dataset.csv <min_supp> <min_conf> `.  The full results are in example-run.txt.

Out of the many rules, we found a few compelling ones:

[Internal,Head] => [Killed] (Conf: 100.0%, Supp: 5.65%)

[Pedestrian,Head] => [Killed] (Conf: 92.73743016759776%, Supp: 8.3%)

[Driver,Internal] => [Killed] (Conf: 98.23008849557522%, Supp: 5.55%)

[Occupant,Internal] => [Killed] (Conf: 98.38709677419355%, Supp: 6.1%)

If you have an internal injury (regardless of being a driver or occupant) and/or a head injury, that will most likely lead death. In addition to that, several other association rules also infer that if the person's invovled in a lethal crash, they are most likely male.

[Occupant,Driver,Killed] => [M] (Conf: 87.93103448275862%, Supp: 7.6499999999999995%)

[Driver,Killed] => [M] (Conf: 86.60287081339713%, Supp: 9.049999999999999%)


[Lap Belt & Harness,M] => [Not Ejected] (Conf: 96.34146341463415%, Supp: 7.9%)

[Driver,Lap Belt & Harness] => [Not Ejected] (Conf: 96.33507853403141%, Supp: 9.2%)

In addition, we can confirm that using a Lap Belt & Harness infers that you will not be ejected from the car. 

