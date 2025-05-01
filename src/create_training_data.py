import os
import json
import pandas as pd
import csv
import matplotlib


DATA_DIR = "full_data"  

# load necessary datasets
def load_data():
    articles = pd.read_csv(os.path.join(DATA_DIR, "articles.csv"), delimiter=',', quotechar='"', encoding='utf-8')
    claims = pd.read_csv(os.path.join(DATA_DIR, "claims.csv"))
    relations = pd.read_csv(os.path.join(DATA_DIR, "relation_annotations.csv"))
    entity_annotations = pd.read_csv(os.path.join(DATA_DIR, "entity_annotations.csv"))
    sources = pd.read_csv(os.path.join(DATA_DIR, "sources.csv"))


    return articles, claims, relations, entity_annotations, sources


# get the reliability rateing for sources out of the value column 
def extract_reliability_rating(value):
    try:
        value_data = json.loads(value)
        if isinstance(value_data, dict) and "value" in value_data: #extract the reliability value is exsits
            reliability = value_data["value"].lower()
            if reliability in ["reliable", "unreliable"]:
                return reliability
            else:
                return "unknown"
    except (json.JSONDecodeError, TypeError):
        pass
    return "unknown"

# creates file for source reliability mapped to sources
def create_source_reliabiliy(entity_annotations, sources):
    entity_annotations = entity_annotations[entity_annotations.annotation_type_id == 1] #filter annotations to only type for source reliability label
    sources = sources.merge(entity_annotations, how='left', left_on='id', right_on='entity_id', suffixes=('_source', '_entity_annotation')) # merge with sources
    sources['value'] = sources['value'].fillna('{}') #remove all empty reliability rateings
    sources['source_reliability'] = sources['value'].apply(extract_reliability_rating)
    sources['source_reliability'] = sources['source_reliability'].fillna('unknown') #any empty reliability rateings replaced with unknown

    reliability_sources = sources[['name', 'source_reliability']]
    reliability_sources.to_csv("data/source_reliability.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig") #create a file for all source reliability
    print("Source reliability data saved as source_reliability.csv")
    return sources

# makes weighted determination for article baised on claims made
def determine_article_veracity(claims):
    claim_weights = {
        'false': 0,
        'mostly-false': 1,
        'mixture': 2,
        'mostly-true': 3,
        'true': 4
    }
    
    #exstracts claim values and gives them weights
    values= []
    for value in claims.values: 
        if value in claim_weights:
            values.append(claim_weights.get(value, -1)) 
    
    if not values: #if no values return unknown
        return 'unknown'

    avg_score = sum(values) / len(values)

    #makes determination for the article from the compiled weights
    if avg_score < 0.5:
        return 'false'
    elif avg_score < 1.5:
        return 'mostly-false'
    elif avg_score < 2.5:
        return 'mixture'
    elif avg_score < 3.5:
        return 'mostly-true'
    else:
        return 'true'

# map claims and reliability to articles
def map_data_to_articles(articles, claims, relations, sources, entity_annotations):
    sources = create_source_reliabiliy(entity_annotations, sources)
    
    articles = articles.merge(sources, left_on='source_id', right_on='id_source', how='left') #merge sources with articles

    relations = relations[['source_entity_id', 'target_entity_id']].rename(columns={'source_entity_id': 'article_id', 'target_entity_id': 'claim_id'}) #rename to prevent mergeing errors
    article_claims = relations.merge(claims, on='claim_id', how='left') #merge the relations with claims

    #determine article label and merge with articles
    article_labels = article_claims.groupby('article_id')['claim_veracity'].apply(determine_article_veracity).reset_index() 
    articles = articles.merge(article_labels, left_on='id', right_on='article_id', how='left')

    articles = articles[['raw_body', "name", 'claim_veracity']] #filter to only raw_body name and determined claim label
    return articles



articles, claims, relations, entity_annotations, sources = load_data()
claims = claims[['id', 'rating']].rename(columns={'id': 'claim_id', 'rating': 'claim_veracity'}) #rename to prevent mergeing errors


dataset = map_data_to_articles(articles, claims, relations, sources, entity_annotations)
dataset = dataset.dropna(subset=['claim_veracity']) #drop any articles with no claim determination

dataset = dataset.dropna(subset=['raw_body']) # drop any articles with empty raw body
dataset = dataset[dataset['raw_body'].str.strip().astype(bool)] #removes any articles that are empty strings


print("Article counts by veracity label:")
print(dataset['claim_veracity'].value_counts())


dataset.to_csv("data/training_data.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig") #save dataset for later use
print("Training dataset saved as training_data.csv")

