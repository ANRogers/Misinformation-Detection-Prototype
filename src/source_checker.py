import pandas as pd

# loads source reliability file 
reliability_df = pd.read_csv('data/source_reliability.csv')
reliability_dict = dict(zip(reliability_df['name'], reliability_df['source_reliability']))

#gets the reliablity of the article source
def check_source_reliability(source_name):
    source_name = source_name.lower().strip()
    return reliability_dict.get(source_name, 'unknown') 

