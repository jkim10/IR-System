import pandas as pd
df = pd.read_csv("original.csv")
df['PERSON_AGE'] = pd.cut(df['PERSON_AGE'], bins=[0, 20, 50, 70,100], include_lowest=True, labels=['0-20', '21-50', '51-70','71-100'])
filtered_columns = df[['PERSON_TYPE', 'PERSON_AGE','PERSON_INJURY','EJECTION','BODILY_INJURY','POSITION_IN_VEHICLE','SAFETY_EQUIPMENT','PED_LOCATION','PED_ACTION','COMPLAINT','PERSON_SEX']]
filtered_columns.to_csv("integrated_dataset.csv",index=False)