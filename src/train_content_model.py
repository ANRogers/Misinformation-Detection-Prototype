import pandas as pd
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from preprocess import clean_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def create_logistic_pipeline():
    # Create a pipeline with logistic regression
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=3
        )),
        ('logistic', LogisticRegression(
            solver='saga', 
            penalty='l2',      
            class_weight='balanced',
            random_state=42,
            max_iter=1000,
            n_jobs=-1           
        ))
    ])
    return pipeline

def create_random_forest_pipline():
    # Create a pipeline with the random forest classifier
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            stop_words='english',
            min_df=3
        )),
        ('randomforest', RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ))
    ])
    return pipeline

#model type options 
# 0 = logistic regression
# 1 = random forest classifier
model_type = 1

# load dataset
dataset = pd.read_csv('data/training_data.csv')

dataset = dataset[dataset['claim_veracity'].isin(['true', 'false'])] #filter to only true and false
dataset['raw_body'] = dataset['raw_body'].fillna('').astype(str) #ensure no empty data to prevent errors
dataset['cleaned'] = dataset['raw_body'].apply(clean_text) #pre-process all artile text

# break up article text and claim veracity
articles_text = dataset['cleaned']
articles_labels = dataset['claim_veracity'].map({'false': 0, 'true': 1}).astype(int)

# split dataset into testing and training data
articles_text_train, articles_text_test, articles_labels_train, articles_labels_test = train_test_split(articles_text, articles_labels, test_size=0.1, random_state=42)

#choose model to train
if model_type == 0:
    pipeline = create_logistic_pipeline()
elif model_type == 1:
    pipeline = create_random_forest_pipline()
else:
    print("ERROR: invalid model type input")
    exit()


# train model on split training data
pipeline.fit(articles_text_train, articles_labels_train)

#predict useing trained model and remaining test data
article_predictions = pipeline.predict(articles_text_test)

#assess accuracy of model
accuracy = accuracy_score(articles_labels_test, article_predictions)

#output performace of trained model
confusion_mtrix = confusion_matrix(articles_labels_test, article_predictions)

print("Model Accuracy: {:.2f}%".format(accuracy * 100))
print("\nClassification Report:\n", classification_report(articles_labels_test, article_predictions, target_names=['Misleading (0)', 'Reliable (1)']))
print("\nConfusion Matrix:\n", confusion_mtrix)

#plot results
labels = ['Misleading', 'Reliable']
plt.figure(figsize=(6, 5))
sns.heatmap(confusion_mtrix, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
plt.tight_layout()
plt.show()
plt.savefig("results/confusion_matrix.png")

# save trained model for later use
joblib.dump(pipeline, 'models/random_forest_pipeline.pkl')
