# BUAN 6390 Project Data Dump (Hospitals 1 to 15); JSON to CSV
import pandas as pd
import json
import numpy as np
from pathlib import Path  

#region (df1) 1-NY-PresQueens: standard_charge_dollar
jsonFile= r"E:/School Project Data/1-NY-PresQueens_raw.json" #replace with your json file and paths
#inspect structure; 143,366 rows
with open(jsonFile, 'r') as f:
    data= json.load(f)

# Normalize hospital locations and addresses (extraneous?)
hospitals_df = pd.DataFrame({
    "hospital_location": data["hospital_location"],
    "hospital_address": data["hospital_address"]
})

# Normalize standard charge information
charges_df = pd.json_normalize(
    data["standard_charge_information"], 
    record_path=["standard_charges", "payers_information"],  # Extract nested payer info
    meta=[
        ["description"],  # Keep track of drug description
        ["code_information"],  # Extract associated codes
        ["standard_charges", "setting"],  # Charge setting (both/inpatient/outpatient)
        ["standard_charges", "gross"],
        ["standard_charges", "discounted_cash"],
        ["standard_charges", "minimum"],
        ["standard_charges", "maximum"]
    ],
    errors="ignore"
)

# Explode `code_information` into separate columns
code_info = pd.json_normalize(data["standard_charge_information"], record_path=["code_information"], meta=["description"])
code_info = code_info.rename(columns={"code": "billing_code", "type": "code_type"})

# Merge codes into charges dataframe
df1 = charges_df.merge(code_info, on="description", how="left")

df1['hospital']='New York Presbyterian Queens' # inserts hospital field to dataframe
df1['zip_code']='11355'
df1['state']='New York'
df1['metroplex']='NYC' # inserts metroplex field to dataframe

df1.count() #6,865,296 records, 612 estimated amount, 1,670,563 standard_charge_dollar rows
df1.groupby(['code_type']).size() #120,144 CPT out of 6,865,296 rows = 1.75%

#refined export to csv
path= Path(r'E:\School Project Data\1-NY-PresQueens_refined.csv') # replace path with your desired system file path
df1.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

#filtered export to csv
df1=df1[df1['code_type']=='CPT'] #filter rows to only CPT
df1=df1.rename(columns={'standard_charges.gross':'gross_charge'}) # renames into gross_charge
df1=df1.rename(columns={'standard_charge_dollar':'insurer_price'}) # renames into insurer_price
df1=df1.rename(columns={'standard_charges.maximum':'max_price'}) #renames in max_price
df1=df1.rename(columns={'standard_charges.discounted_cash':'discounted_cash'})
df1=df1.rename(columns={'additional_payer_notes':'additional_generic_notes'}) # renames into generic notes
df1=df1[['metroplex', 'state', 'zip_code', 'hospital',
         'billing_code', 'gross_charge','insurer_price', 'max_price', 'discounted_cash',
         'description','payer_name','plan_name','additional_generic_notes']]
df1.loc[df1['payer_name'] == 'Ambetter from Fidelis Care', 'payer_name'] = 'Ambetter'
df1.loc[df1['payer_name'] == 'EmblemHealth', 'payer_name'] = 'Emblem Health'


path= Path(r'E:\School Project Data\1-NY-PresQueens.csv') # replace path with your desired system file path
df1.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

#endregion

#region (df3) 3-9-NYPres: 10 fields, standard_charge_dollar, one set of codes
#load JSON data
jsonFile= r"E:/School Project Data/3-9-NY-Pres_raw.json" #replace with your json file and paths
#jsonFile= r"" #replace with your json file and paths

#inspect structure; 143,366 rows
with open(jsonFile, 'r') as f:
    data= json.load(f)
#print(json.dumps(data, indent=4)) # turns out to be nested

# Normalize hospital locations and addresses (extraneous?)
hospitals_df = pd.DataFrame({
    "hospital_location": data["hospital_location"],
    "hospital_address": data["hospital_address"]
})

# Normalize standard charge information
charges_df = pd.json_normalize(
    data["standard_charge_information"], 
    record_path=["standard_charges", "payers_information"],  # Extract nested payer info
    meta=[
        ["description"],  # Keep track of drug description
        ["code_information"],  # Extract associated codes
        ["standard_charges", "setting"],  # Charge setting (both/inpatient/outpatient)
        ["standard_charges", "gross"],
        ["standard_charges", "discounted_cash"],
        ["standard_charges", "minimum"],
        ["standard_charges", "maximum"]
    ],
    errors="ignore"
)
charges_df['code_information'][charges_df['code_information'].str.len().idxmax()]

# Explode `code_information` into separate columns
code_info = pd.json_normalize(data["standard_charge_information"], record_path=["code_information"], meta=["description"])
code_info = code_info.rename(columns={"code": "billing_code", "type": "code_type"})

# Merge codes into charges dataframe
df = charges_df.merge(code_info, on="description", how="left")

df['hospital']='New York Presbyterian System' # inserts hospital field to front of dataframe
df['zip_code']='multiple'
df['state']='New York' 
df['metroplex']='NYC' # inserts metroplex field to dataframe

#Exploratory Data Analysis (7,583,316 records for 3-9-NYPres)
agg= df.groupby(['description','payer_name','plan_name']).size(); agg #7,393,776 unique combinations of description/provider/plan
df.count() # outputs number of non-null records by field

# estimated amount and standard_charge_algorithm is mainly null
# standard_charge_dollar is majority null but is the most available unique field for charges
#      (usually in cases where methodology= ['other', 'fee schedule'] and/or additional_payer_notes=['not separately payable', 'not applicable'...]
# standard_charges.xxx fields are common across payers and plans for a given description and therefore not useful

#refined export to csv
path= Path(r'E:\School Project Data\3-9-NY-Pres_refined.csv') # replace path with your desired system file path
df.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

#filtered export to csv
df.groupby(['code_type']).size() #242,996 CPT out of 7,583,316 rows = 3.20%
df=df[df['code_type']=='CPT'] #filter rows to only CPT
df=df.rename(columns={'standard_charges.gross':'gross_charge'})
df=df.rename(columns={'standard_charge_dollar':'insurer_price'})
df=df.rename(columns={'standard_charges.maximum':'max_price'}) #renames in max_price
df=df.rename(columns={'standard_charges.discounted_cash':'discounted_cash'})
df=df.rename(columns={'additional_payer_notes':'additional_generic_notes'})

df3=df[['metroplex','state','zip_code','hospital',
        'billing_code', 'gross_charge','insurer_price','max_price', 'discounted_cash',
        'description','payer_name','plan_name','additional_generic_notes']]
df3.loc[df3['payer_name'] == 'Ambetter by Fidelis Care', 'payer_name'] = 'Ambetter'
df3.loc[df3['payer_name'] == 'EmblemHealth', 'payer_name'] = 'Emblem Health'
df3.loc[df3['payer_name'] == 'MVP HEALTH', 'payer_name'] = 'MVP'

path= Path(r'E:\School Project Data\3-9-NY-Pres.csv') # replace path with your desired system file path
df3.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

## alternative: partitioned CSV output
'''
chunk_size=1000000
num_chunks= len(df)//chunk_size+1
for i in range(num_chunks):
    start_row= i*chunk_size
    end_row= start_row + chunk_size
    chunk=df.iloc[start_row:end_row]
    chunk.to_csv(f"E:/School Project Data/NY-Presbyterian_part_{i+1}.csv", index=False)
'''
#endregion

#region (df10) 10-Newark-wayne: 16 fields, estimated_amount, four sets of codes (Code 2 has CPT, Code 3 is ONLY RC, Code 4 is mostly null)
#load csv newark-wayne
df10 = pd.read_csv(r"E:/School Project Data/10-Newark-Wayne_raw.csv", skiprows=2, encoding="latin1")  # Use raw string (r"")
'''
df10=df10[['description','payer_name','plan_name','estimated_amount','setting', # estimated amount is used since standard_charge|gross/discounted are equal between plans/payers
        'code|1','code|1|type','code|2','code|2|type', # 4 sets of fields for codes and code types
        'code|3','code|3|type','code|4','code|4|type', #standard charges are skipped for since they are common across payers/plans for a given description
        'standard_charge|methodology','additional_generic_notes']] 
'''
df10.count()
df10.groupby(['code|1|type']).size()
df10.groupby(['code|2|type']).size() #code 2 has CPT; 2,774,270 / 4,374,058= 63.4%

#exploratory data analysis
#df10=df10[df10['estimated_amount']!=999999999] # usually flagged as not separately payable
df10['estimated_amount'] = df10['estimated_amount'].replace(999999999, np.nan) # replaces with None
df10.sort_values(by='estimated_amount', ascending=False)[['estimated_amount']] #verifies that other high values are not mistakenly removed
#standard charges are skipped for since they are common across payers/plans for a given description

df10['hospital']='Newark-Wayne Community Hospital' # inserts hospital name into dataframe
df10['zip_code']='14513'
df10['state']='New York' # inserts state field to dataframe
df10['metroplex']='NYC' # inserts metroplex field to dataframe

#refined export to csv
path= Path(r'E:\School Project Data\10-Newark-Wayne_refined.csv') # replace path with your desired system file path
df10.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

#filtered export to csv
df10=df10[df10['code|2|type']=='CPT']
df10=df10.rename(columns={'code|2':'billing_code'})
df10=df10.rename(columns={'standard_charge|gross':'gross_charge'})
df10=df10.rename(columns={'estimated_amount':'insurer_price'})
df10=df10.rename(columns={'standard_charge|max':'max_price'})
df10=df10.rename(columns={'standard_charge|discounted_cash':'discounted_cash'})
df10=df10[['metroplex','state','zip_code','hospital',
            'billing_code','gross_charge', 'insurer_price', 'max_price', 'discounted_cash',
            'description','payer_name','plan_name','additional_generic_notes']] # estimated amount is used since standard_charge|gross/discounted are equal between plans/payers
df10.loc[df10['payer_name'] == 'AETNA [100]', 'payer_name'] = 'Aetna'
df10.loc[df10['payer_name'] == 'EMBLEM GHI [113]', 'payer_name'] = 'Emblem Health'
df10.loc[df10['payer_name'] == 'MOLINA HEALTHCARE OF NY [188]', 'payer_name'] = 'Molina Healthcare'
df10.loc[df10['payer_name'] == 'MVP [109]', 'payer_name'] = 'MVP'



path= Path(r'E:\School Project Data\10-Newark-Wayne.csv') # replace path with your desired system file path
df10.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

#endregion

#region (df11) 11-NewarkBeth: 10 fields, estimated_amount, one set of codes (+standard_charge|gross for completeness)
#loading csv newarkbeth
df11= pd.read_csv(r"E:/School Project Data/11-NewarkBeth_raw.csv", skiprows=2, encoding="latin1", low_memory=False) #small; 108,533 rows
df11.count() # code|2 and code|2|type are completely empty/null and are thus dropped
df11[(df11[' estimated_amount '].isnull()) & (df11[' standard_charge|gross '].notnull())] # these + estimated amount = 108,533 rows BUT these are all for 'not separately payable'

'''
df11=df11[['description','payer_name','plan_name',' estimated_amount ','setting', #estimated amount is used since it has far less nulls and differs between plans/payers
         ' standard_charge|gross ',
         'code|1','code|1|type', # a given description can have multiple codes
         'standard_charge|methodology','additional_generic_notes']] # additional notes is mostly null
'''
df11['hospital']='Newark Beth Israel Medical Center'
df11['zip_code']='07112'
df11['state']='New Jersey'
df11['metroplex']='NYC'

#refined export to csv
path= Path(r'E:\School Project Data\11-NewarkBeth_refined.csv') # replace path with your desired system file path
df11.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

#filtered export to csv
df11=df11.rename(columns={' standard_charge|gross ':'gross_charge'})
df11=df11.rename(columns={' estimated_amount ':'insurer_price'})
df11=df11.rename(columns={' standard_charge|max ':'max_price'})
df11=df11.rename(columns={' standard_charge|discounted_cash ':'discounted_cash'})
df11=df11.rename(columns={'code|1':'billing_code'}) # renames into billing_code
df11=df11[df11['code|1|type']=='CPT'] # 81,949 CPT out of 108,533= 75.5% CPT
df11=df11[['metroplex', 'state', 'zip_code','hospital', 
            'billing_code', 'gross_charge', 'insurer_price', 'max_price', 'discounted_cash',
            'description', 'payer_name', 'plan_name', 'additional_generic_notes']]
path= Path(r'E:\School Project Data\11-NewarkBeth.csv') # replace path with your desired system file path
df11.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed
#endregion

#region (df12) 12-UniversityHospital: 12 fields, standard_charge|negotiated_dollar, two sets of codes (Code 1 has CPT, Code 2 is mostly null)
df12= pd.read_csv(r"E:/School Project Data/12-UniversityHospital_raw.csv", skiprows=2, encoding="latin1", low_memory=False) #small; 101,996 rows
df12.count() # code|2 are very small, estimated_amount is mostly null

'''df12=df12[['description','payer_name','plan_name','standard_charge|negotiated_dollar','setting', # standard_charge|negotiated_dollar is used since it has far less nulls and differs between plans/payers
         'code|1','code|1|type', 'code|2','code|2|type', # two sets of fields for code and code type
         'standard_charge|methodology','additional_generic_notes']] # additional notes is 3/4 null
'''

df12['hospital']='University Hospital'
df12['zip_code']='07103'
df12['state']='New Jersey'
df12['metroplex']='NYC'
# standard_charge|negotiated_dollar has empty values when the notes read: 'Drugs are paid at 100% of the AWP'

#refined export to csv
path= Path(r'E:\School Project Data\12-UniversityHospital_refined.csv') # replace path with your desired system file path
df12.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # when opening csv with excel, some values have apostophe in front

#filtered export to csv
df12=df12[df12['code|1|type']=='CPT'] # 70,970 CPT out of 101,996= 69.6% CPT
df12=df12.rename(columns={'code|1':'billing_code'})
df12=df12.rename(columns={'standard_charge|gross':'gross_charge'}) 
df12=df12.rename(columns={'standard_charge|negotiated_dollar':'insurer_price'})
df12=df12.rename(columns={'standard_charge|max':'max_price'})
df12=df12.rename(columns={'standard_charge|discounted_cash':'discounted_cash'})
df12=df12[['metroplex', 'state', 'zip_code', 'hospital', 
            'billing_code', 'gross_charge', 'insurer_price', 'max_price', 'discounted_cash',
            'description','payer_name','plan_name','additional_generic_notes']]
df12.loc[df12['payer_name'] == 'Consumer', 'payer_name'] = 'Consumer Health Network'

path= Path(r'E:\School Project Data\12-UniversityHospital.csv') # replace path with your desired system file path
df12.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # when opening csv with excel, some values have apostophe in front

#endregion

#region (df13) 13-SilverLakeHospital: DISCARDED
df13= pd.read_csv(r"E:/School Project Data/13-SilverLakeHospital_raw.csv", skiprows=15, encoding="latin1", low_memory=False) #tiny; 1000 rows
df13.count() # does not include any detail on payer/plan; do we still use???
#endregion

#region (df14) 14-SaintMichaels: 9 fields, standard_charge_dollar, two set of codes, no 'additional notes' field
jsonFile= r"E:/School Project Data/14-SaintMichaels_raw.json" #replace with your json file and paths
with open(jsonFile, 'r', encoding='utf-8-sig') as f:
    data= json.load(f)

# Normalize standard charge information
charges_df = pd.json_normalize(
    data["standard_charge_information"], 
    record_path=["standard_charges", "payers_information"],  # Extract nested payer info
    meta=[
        ["description"],  # Keep track of drug description
        "code_information",  # Extract associated codes
        ["standard_charges", "setting"],  # Charge setting (both/inpatient/outpatient)
        ["standard_charges", "gross_charge"], #differs from NY-Pres (gross)
        ["standard_charges", "discounted_cash"], # not omni-present
        ["standard_charges", "minimum"],
        ["standard_charges", "maximum"]
    ],
    errors="ignore"
)

# Extract first and second code/type pairs
charges_df["code|1"] = charges_df["code_information"].apply(lambda x: x[0]['code'] if len(x) > 0 else None)
charges_df["code|1|type"] = charges_df["code_information"].apply(lambda x: x[0]['type'] if len(x) > 0 else None)
charges_df["code|2"] = charges_df["code_information"].apply(lambda x: x[1]['code'] if len(x) > 1 else None)
charges_df["code|2|type"] = charges_df["code_information"].apply(lambda x: x[1]['type'] if len(x) > 1 else None)

# Merge codes into charges dataframe
df14 = charges_df
df14.count() # 3,928,795 rows
df14['standard_charges.gross_charge']=df14['standard_charges.gross_charge'].astype(float)
df14['standard_charge_dollar']=df14['standard_charge_dollar'].astype(float)
df14['hospital']='Saint Michaels Medical Center'
df14['zip_code']='07102'
df14['state']='New Jersey'
df14['metroplex']='NYC'

#refined export to csv
path= Path(r'E:\School Project Data\14-SaintMichaels_refined.csv') # replace path with your desired system file path
df14.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed, issue with apostrophe

#filtered export to csv
df14=df14[df14['code|1|type']=='CPT'] #CPT only exists in the first code column; 153978/207917= 74% CPT
df14=df14.rename(columns={'code|1':'billing_code'})
df14=df14.rename(columns={'standard_charges.gross_charge':'gross_charge'}) #274 ROWS WITH !!BLANK!! GROSS_CHARGES (two drugs: abatacept and bupivacaine)
df14=df14.rename(columns={'standard_charge_dollar':'insurer_price'}) 
df14=df14.rename(columns={'standard_charges.maximum':'max_price'}) 
df14=df14.rename(columns={'standard_charges.discounted_cash':'discounted_cash'}) 
df14=df14.rename(columns={'methodology':'additional_generic_notes'}) # substitutes missing notes column with methodology for context
df14=df14[['metroplex','state','zip_code','hospital',
        'billing_code','gross_charge', 'insurer_price', 'max_price', 'discounted_cash',
        'description','payer_name','plan_name','additional_generic_notes']] #estimated_amount has a lot of 999999999 values for no discernable reason
df14.loc[df14['payer_name'] == 'Cigna', 'payer_name'] = 'Cigna Healthcare'

         # no equivalent to additional notes (standard_charge_algorithm is only 'Not To Exceed $x' where x is some dollar amount)
path= Path(r'E:\School Project Data\14-SaintMichaels.csv') # replace path with your desired system file path
df14.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed, issue with apostrophe

#endregion

#region (df15) 15-JerseyCity: 10 fields, estimated_amount, one set of codes
# similar to 11-NewarkBeth
df15= pd.read_csv(r"E:/School Project Data/15-JerseyCity_raw.csv", skiprows=2, encoding="latin1", low_memory=False) #small; 88,791 rows
df15.count() # code|2, code|2|type, standard_charge|discounted_cash and standard_charge|negotiated algorithm have 0 values
df15.groupby(['code|1|type']).size() #has CPT; 64,055 / 88,791 = 72.1%
# standard_charge|negotiated_dollar might be more accurate per the github data dictionary template, but not 
'''
df15=df15[['description', 'payer_name', 'plan_name', ' estimated_amount ', 'setting', # estimate_amount is most common field that differs between payer/plan
         'code|1','code|1|type', # one set of fields for code and code type
         'standard_charge|methodology', 'additional_generic_notes']] # additional notes is mostly null
'''
#refined export to csv
df15['hospital']='Jersey City Medical Center'
df15['zip_code']='07302'
df15['state']='New Jersey'
df15['metroplex']='NYC'
path= Path(r'E:\School Project Data\15-JerseyCity_refined.csv') # replace path with your desired system file path
df15.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed

#filtered export to csv
df15=df15[df15['code|1|type']=='CPT'] #filters only CPT
df15=df15.rename(columns={' standard_charge|gross ':'gross_charge'})
df15=df15.rename(columns={' estimated_amount ':'insurer_price'})
df15=df15.rename(columns={' standard_charge|max ':'max_price'})
df15=df15.rename(columns={' standard_charge|discounted_cash ':'discounted_cash'})
df15=df15.rename(columns={'code|1':'billing_code'})
df15=df15[['metroplex','state','zip_code','hospital',
            'billing_code', 'gross_charge','insurer_price','max_price', 'discounted_cash',
            'description','payer_name','plan_name','additional_generic_notes']]
path= Path(r'E:\School Project Data\15-JerseyCity.csv') # replace path with your desired system file path
df15.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed
#endregion

#region (df31) 31-SaintJosephs: standard_charge|negotiated_dollar
df31= pd.read_csv(r"E:/School Project Data/31-SaintJosephs_raw.csv", skiprows=2, encoding="latin1", low_memory=False) #small; 96,634 rows
df31.count() # a lot missing codes
df31.groupby(['code|[i]|type']).size()

#refined export to csv
df31['hospital']='Saint Josephs Medical Center'
df31['zip_code']='10701'
df31['state']='New York'
df31['metroplex']='NYC'
path= Path(r'E:\School Project Data\31-SaintJosephs_refined.csv') # replace path with your desired system file path
df31.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed

#filtered export to csv, convert payer_names
df31=df31[df31['code|[i]|type']=='CPT'] #filters only CPT; 42,674 rows (44%)
df31=df31.rename(columns={'standard_charge|gross':'gross_charge'})
df31=df31.rename(columns={'standard_charge|negotiated_dollar':'insurer_price'})
df31=df31.rename(columns={'standard_charge|max':'max_price'})
df31=df31.rename(columns={'standard_charge|discounted_cash':'discounted_cash'})
df31=df31.rename(columns={'code|[i]':'billing_code'})
df31=df31[['metroplex','state','zip_code','hospital',
            'billing_code', 'gross_charge','insurer_price','max_price', 'discounted_cash',
            'description','payer_name','plan_name','additional_generic_notes']]
df31.loc[df31['payer_name'] == '1199 SEIU ', 'payer_name'] = '1199 SEIU Funds'
df31.loc[df31['payer_name'] == 'AETNA ', 'payer_name'] = 'Aetna'
df31.loc[df31['payer_name'] == 'EMBLEM ', 'payer_name'] = 'Emblem Health'
df31.loc[df31['payer_name'] == 'EMBLEM HEALTH ', 'payer_name'] = 'Emblem Health'
df31.loc[df31['payer_name'] == 'FIDELIS ', 'payer_name'] = 'Fidelis Care'
df31.loc[df31['payer_name'] == 'MOLINA HEALTHCARE ', 'payer_name'] = 'Molina Healthcare'

path= Path(r'E:\School Project Data\31-SaintJosephs.csv') # replace path with your desired system file path
df31.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed
#endregion

#region (df32) 32-StonyBrookUniversityHospital: DISCARDED 301 columns...needs to be unexploded and also data seems TERRIBLE in quality
df32= pd.read_csv(r"E:/School Project Data/32-StonyBrookUniversityHospital_raw.csv", skiprows=2, encoding="latin1", low_memory=False) #very small; 43,349 rows
df32.count() # a lot missing codes

# filtering out for CPT now for ease of unexploding dataset
df32=df32[df32['code|1|type']=='CPT']
# looks like the modifier column never affects any payer prices but for some reason does affect standard_charge|gross and standard_charge|discounted_cash
# problem is that the quantity of modifiers is never certain and there can be no modifiers and there also can be ONLY modifiers (we could try taking only one)
# additionally, most of the usable prices (estimated_amount) is the simple code of 999999999
# the next most available price related field is negotiated_percentage, but multiplying it by gross_charge is never congruent with estimated_amount even when its not 999999999

#unexploding columns, 6 repeated columns, 288 columns/6 = 48 payer/plans
# [standard_charge|negotiated_dollar, standard_charge|negotiated_percentage, standard_charge|negotiated_algorithm, estimated_amount, standard_charge|methodology, additional_payer_notes]
# Identify the columns that need melting (that aren't unexploded)
id_vars = ['description', 'code|1', 'code|1|type', 'modifiers', 'setting', 
           'drug_unit_of_measurement', 'drug_type_of_measurement',
           'standard_charge|gross', 'standard_charge|discounted_cash',
           'standard_charge|min', 'standard_charge|max', 'additional_generic_notes',
           'billing_class']
value_vars = [col for col in df32.columns if col not in id_vars]
# Melt the dataframe
df32_melted = df32.melt(id_vars=id_vars, value_vars=value_vars,
                    var_name="payer_info", value_name="value")
# Split the "payer_info" column
split_cols = df32_melted["payer_info"].str.split("|", expand=True)
# Now assign the parts to new columns (max 5 parts usually)
df32_melted["charge_prefix"] = split_cols[0]
df32_melted["payer_name"] = split_cols[1]
df32_melted["plan_name"] = split_cols[2]
df32_melted["charge_suffix"] = split_cols[3].fillna("")
df32_melted["true_column_name"] = split_cols[0] +"|"+split_cols[3].fillna("")
df32_filteredP = df32_melted[df32_melted['value'].notna()]
print(len(df32_filteredP))
df32_deduped = df32_filteredP.drop_duplicates(
    subset=[col for col in df32_filteredP.columns if col not in ['value']])
df32_pivoted = df32_deduped.pivot(
    index=[col for col in df32_melted.columns if col not in ['true_column_name', 'value']],
    columns='true_column_name', values='value',).reset_index()
index_columns = ['description', 'code|1', 'code|1|type', 'modifiers', 'setting', 
           'drug_unit_of_measurement', 'drug_type_of_measurement',
           'standard_charge|gross', 'standard_charge|discounted_cash',
           'standard_charge|min', 'standard_charge|max', 'additional_generic_notes',
           'billing_class', 'payer_name', 'plan_name']

df32_collapsed = df32_pivoted.groupby(index_columns, dropna=False).first().reset_index()
df32=df32_collapsed #looks correct as far as the data exploding looks but... data itself seems unhelpful (estimated_amount=999999999 is 497,869 of 587,665 rows)

path= Path(r'E:\School Project Data\32-test.csv') # replace path with your desired system file path
df32.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed




#endregion

#region (df33) 33-WayneMemorial
df33= pd.read_csv(r"E:/School Project Data/33-WayneMemorial_raw.csv", skiprows=2, encoding="latin1", low_memory=False)
df33.count() 

#unexploding columns, 126 repeated columns/6 per = 21 payer/plans
# [standard_charge|negotiated_percentage, standard_charge|negotiated_dollar, standard_charge|negotiated_algorithm, standard_charge|methodology, additional_payer_notes, estimated_amount]
# Identify the columns that need melting (that aren't unexploded)
id_vars = ['description', 'code|1', 'code|1|type', 'code|2', 'code|2|type', 'modifiers', 'setting',
           'billing_class','drug_unit_of_measurement', 'drug_type_of_measurement',
           'standard_charge|gross', 'standard_charge|discounted_cash',
           'standard_charge|min', 'standard_charge|max', 'additional_generic_notes']
value_vars = [col for col in df33.columns if col not in id_vars]
# Melt the dataframe
df33_melted = df33.melt(id_vars=id_vars, value_vars=value_vars,
                    var_name="payer_info", value_name="value")
# Split the "payer_info" column
split_cols = df33_melted["payer_info"].str.split("|", expand=True)
# Now assign the parts to new columns (max 5 parts usually)
df33_melted["charge_prefix"] = split_cols[0]
df33_melted["payer_name"] = split_cols[1]
df33_melted["plan_name"] = split_cols[2]
df33_melted["charge_suffix"] = split_cols[3].fillna("")
df33_melted["true_column_name"] = split_cols[0] +"|"+split_cols[3].fillna("")
df33_filteredP = df33_melted[df33_melted['value'].notna()]
print(len(df33_filteredP))
df33_deduped = df33_filteredP.drop_duplicates(
    subset=[col for col in df33_filteredP.columns if col not in ['value']])
df33_pivoted = df33_deduped.pivot(
    index=[col for col in df33_melted.columns if col not in ['true_column_name', 'value']],
    columns='true_column_name', values='value',).reset_index()
index_columns= ['description', 'code|1', 'code|1|type', 'code|2', 'code|2|type', 'modifiers', 'setting',
           'billing_class','drug_unit_of_measurement', 'drug_type_of_measurement',
           'standard_charge|gross', 'standard_charge|discounted_cash',
           'standard_charge|min', 'standard_charge|max', 'additional_generic_notes',
           'payer_name', 'plan_name']
df33_collapsed = df33_pivoted.groupby(index_columns, dropna=False).first().reset_index()
df33=df33_collapsed

df33['hospital']='Wayne Memorial Hospital' # inserts hospital field to dataframe
df33['zip_code']='18431'
df33['state']='Pennsylvania'
df33['metroplex']='NYC' # inserts metroplex field to dataframe

#refined export to csv
path= Path(r'E:\School Project Data\33-WayneMemorial_refined.csv') # replace path with your desired system file path
df33.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed

#filtered csv
df33=df33[df33['code|1|type']=='CPT']
df33=df33.rename(columns={'standard_charge|gross':'gross_charge'})
df33=df33.rename(columns={'estimated_amount|':'insurer_price'})
df33=df33.rename(columns={'standard_charge|max':'max_price'})
df33=df33.rename(columns={'standard_charge|discounted_cash':'discounted_cash'})
df33=df33.rename(columns={'code|1':'billing_code'})
df33=df33[['metroplex','state','zip_code','hospital',
            'billing_code', 'gross_charge','insurer_price','max_price', 'discounted_cash',
            'description','payer_name','plan_name','additional_payer_notes|']]
df33=df33.rename(columns={'additional_payer_notes|':'additional_generic_notes'}) #generic notes in normal dataframe are blank, payer notes have info
path= Path(r'E:\School Project Data\33-WayneMemorial.csv') # replace path with your desired system file path
df33.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed
#endregion

###### very big (not on record xd) also not NYC
#region (df16) 16-AscensionSetonAustin: x fields, estimate_amount, two sets of codes
df16= pd.read_csv(r"E:/School Project Data/16-AscensionSetonAustin_raw.csv", skiprows=2, encoding="latin1", low_memory=False) #very large; 18,965,898 rows
df16.count() #payer_name and plan_name look to be semi-redundant
df16=df16[['description', 'payer_name', 'plan_name', 'estimated_amount', 'setting', # estimate_amount is most common field that differs between payer/plan
         'code|1','code|1|type', 'code_2', 'code_2_type', # two sets of fields for code and code type, the second set uses _ instead of |
         'standard_charge|methodology', 'additional_generic_notes']]
df16=df16.rename(columns={'code_2':'code|2', 'code_2_type':'code|2|type'}) # makes the second set of codes consistent
df16['Hospital']='Ascension Seton Austin' # RAW FILE ONLY LISTS ASCENSION SETON
reorder= ['Hospital']+[col for col in df16.columns if col !='Hospital'] # reorders column
df16=df16[reorder]
df16.count()

path= Path(r'E:\School Project Data\16-AscensionSetonAustin.csv') # replace path with your desired system file path
df16.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed
#endregion

###### strange JSON, all on one line, also not NYC
#region (df18) 18-SaintDavidSouth: 15 fields, estimated_amount AND standard_Charge_dollar, two set of codes, BOTH WITH CPT!!!
#LOADS raw JSON
jsonFile= r"E:/School Project Data/18-SaintDavidSouth_raw.json"
with open(jsonFile, "r", encoding="utf-8-sig") as f:
    data = json.loads(f.read())  # Parse JSON

#CREATES readable json (not necessary if you've already have the readable json in the directory)
with open("E:/School Project Data/18-SaintDavidSouth_readable.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

#LOADs readable json into VSCode
jsonFile= r"E:/School Project Data/18-SaintDavidSouth_readable.json" #replace with your json file and paths
with open(jsonFile, "r", encoding="utf-8-sig") as f:
    data = json.load(f)  # Parse JSON

# Extract `standard_charge_information`
standard_charges = data.get("standard_charge_information", [])
# Collect all valid `payers_information` entries along with `code_information`
valid_entries = []
for charge in standard_charges:
    codes = charge.get("code_information", [])  # Extract codes (list of dicts)
    # Extract up to two codes and types
    code_1 = codes[0].get("code", "") if len(codes) > 0 else ""
    code_2 = codes[1].get("code", "") if len(codes) > 1 else ""
    code_type_1 = codes[0].get("type", "") if len(codes) > 0 else ""
    code_type_2 = codes[1].get("type", "") if len(codes) > 1 else ""

    for std_charge in charge.get("standard_charges", []):
        if "payers_information" in std_charge:  # Ensure the key exists
            for payer in std_charge["payers_information"]:
                valid_entries.append({
                    **payer,  # Extract payer info
                    "description": charge["description"],  # Keep track of description
                    "code|1": code_1,  # First code
                    "code|2": code_2,  # Second code (if exists)
                    "code|1|type": code_type_1,  # First code type
                    "code|2|type": code_type_2,  # Second code type (if exists)
                    "setting": std_charge.get("setting"),  
                    "gross_charge": std_charge.get("gross_charge"),  
                    "discounted_cash": std_charge.get("discounted_cash"),  
                    "minimum": std_charge.get("minimum"),  
                    "maximum": std_charge.get("maximum")  
                })
                    
# Convert to DataFrame
df18 = pd.DataFrame(valid_entries)
df18.groupby(['code|1|type']).size() # has CPT: 1,211,430
df18.groupby(['code|2|type']).size() # has CPT: 827,077
df18.count() #estimated amount and standard_charge_(algorithm/percentage); !!estimated_amount combined with standard_charge_dollar accounts for ALL!!

#df18=df18[(df18['code|1|type']=='CPT') | (df18['code|2|type']=='CPT')] # keeps CPT if they are in either column

# splitting dataframe into both code columns of CPT only
df18code1= df18[df18['code|1|type']=='CPT']
df18code1=df18code1.rename(columns={'code|1':'billing_code'}) # renames into billing_code
df18code1=df18code1[['billing_code','standard_charge_dollar','estimated_amount','description','payer_name','plan_name','additional_payer_notes']]
df18code2= df18[df18['code|2|type']=='CPT']
df18code2=df18code2.rename(columns={'code|2':'billing_code'}) # renames into billing_code
df18code2=df18code2[['billing_code','standard_charge_dollar','estimated_amount','description','payer_name','plan_name','additional_payer_notes']]

df18code = pd.concat([df18code1, df18code2], axis=0, ignore_index=True) #recombines them into one column

# splitting dataframe into both price columns (standard_charge_dollar and estimated_amount)
df18price1=df18code[['billing_code','standard_charge_dollar','description','payer_name','plan_name','additional_payer_notes']]
df18price1.dropna(subset=['standard_charge_dollar'], inplace=True)
df18price1=df18price1.rename(columns={'standard_charge_dollar':'price'}) # renames into price
df18price2=df18code[['billing_code','estimated_amount','description','payer_name','plan_name','additional_payer_notes']]
df18price2.dropna(subset=['estimated_amount'], inplace=True)
df18price2=df18price2.rename(columns={'estimated_amount':'price'}) # renames into price

df18price = pd.concat([df18price1, df18price2], axis=0, ignore_index=True) #recombines them into one column

df18price['Hospital']='Saint Davids South Austin Medical Center'
df18price=df18price.rename(columns={'additional_payer_notes':'additional_generic_notes'}) # renames into price
df18=df18price[['Hospital','billing_code','price','description','payer_name','plan_name','additional_generic_notes']]

path= Path(r'E:\School Project Data\18-SaintDavidSouth.csv') # replace path with your desired system file path
df18.to_csv(path, index=False, chunksize=1000000)  # Adjust chunk size as needed

#endregion


#region NYC metro dataframe
dataPath=Path(r"E:/School Project Data/") # file directory where hospital data is stored
dataNames=['1-NY-PresQueens.csv', '3-9-NY-Pres.csv', '10-Newark-Wayne.csv',
           '11-NewarkBeth.csv', '12-UniversityHospital.csv', '14-SaintMichaels.csv',
            '15-JerseyCity.csv', '31-SaintJosephs.csv', '33-WayneMemorial.csv'] #list of filtered files
hospital_dfs=[] #empty list to collect each hospital's filtered data
for filename in dataNames: #loads each filtered dataset into a list
    hospital_data=pd.read_csv(dataPath/filename, dtype={4: str}, encoding="latin1")
    hospital_dfs.append(hospital_data)
mdf= pd.concat(hospital_dfs, axis=0, ignore_index=True) # metroDataFrame; stacks the list of hospital data into one dataframe
path= Path(r'E:\School Project Data\Consolidated_NYC_Data.csv') # replace path with your desired system file path
mdf.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed
#endregion

#region exploratory data analysis section
path= Path(r'E:\School Project Data\query.csv') # replace path with your desired system file path

result=mdf.groupby(['hospital','payer_name','plan_name','billing_code','description']).agg({'insurer_price':'mean'}).sort_values(['insurer_price'], ascending=False).reset_index(); result

result = (mdf[mdf['billing_code'] == '42100'].dropna(subset=['insurer_price']).groupby(['hospital', 'payer_name', 'plan_name', 'billing_code', 'description'])
          .agg({'insurer_price': 'max'}).sort_values(['insurer_price'], ascending=False).reset_index()); result
path= Path(r'E:\School Project Data\test.csv') # replace path with your desired system file path
result.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed

#examine payer/plan names for consistency across hospitals
result=mdf.groupby(['hospital','payer_name','plan_name']).agg({'insurer_price':'mean'}).sort_values(['payer_name','plan_name'], ascending=True).reset_index(); result

# fidelis care for df10 has 4 separate payers for Fidelis (worth consolidating?)
# first health coventry and first health for df1 and df3 appear to be the same thing via google but are nevertheless separate (worth consolidating?)
# horizon bcbs and horizon are owned by same parent but are different plans; df11 and df15 have only Horizon BCBS while df12 and df14 have Horizon, where some plans are not BCBS

result=mdf.groupby(['state','hospital','payer_name']).agg({'insurer_price':'mean'}).sort_values(['state','hospital','insurer_price'], ascending=False).reset_index(); result



path= Path(r'E:\School Project Data\payer_name unifier.csv') # replace path with your desired system file path
result.to_csv(path, index=False, chunksize=1000000, float_format='%.15g')  # Adjust chunk size as needed

#endregion