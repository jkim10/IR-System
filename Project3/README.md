# Extract Association Rules from NYC Open Data
By Justin Kim(jyk2149) and Mavis Athene U Chen(mu2288)

## Files in Submission
- proj3.tar.gz
    - extract_associations.py
- integrated_dataset.csv
- example_run.txt
- README.md

## How to Run
```bash
    python3 extract_associations.py integrated_dataset.csv <min_supp> <min_conf>
```


## Integrated Dataset Description
We used the [https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Person/f55k-p6yu](Motor Vehicle Collisions - Person) dataset from NYC Open Data, which contains details for people involved in the crash. We want to investigate vehicles collision injuries and see if we can help mitigate certain types of injuries in the future. For example, we want to predict any associations between type of injury and their role in the crash (driver, occupant, pedestrian, etc.). The dataset is very large so we sampled 2000 out of the 4.24M rows. In addition, we also removed unecessary columns "Collision ID", "Crash Date", "Person ID", etc. that would not play a role in the association rules. We chose 11 out of the 21 columns as our "market basket". The columns remaining are 'PERSON_TYPE', 'PERSON_AGE', 'PERSON_INJURY', 'EJECTION', 'BODILY_INJURY', 'POSITION_IN_VEHICLE', 'SAFETY_EQUIPMENT', 'PED_LOCATION', 'PED_ACTION', 'COMPLAINT', and 'PERSON_SEX'.

## Internal Design of Project
We have implemented the standard apriori algorithm mentioned in 3. of Association Rule Mining Algorithm from the homework post. That is we used the algorithm from Section 2.1 of the [http://www.cs.columbia.edu/~gravano/Qual/Papers/agrawal94.pdf](Agrawal and Srikant paper in VLDB 1994), without the subset function (section 2.1.1).  

## Sample Run and Result Discussions
