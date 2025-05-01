import joblib
from preprocess import clean_text
from source_checker import check_source_reliability

# load trained model
model = joblib.load('models/random_forest_pipeline.pkl')

def predict_article(article_text):
    # clean article text to remove html components
    cleaned_article = clean_text(article_text)

    # use trained model to make a prediction
    article_prediction = model.predict([cleaned_article])[0]
    misleading_probability, reliable_probability = model.predict_proba([cleaned_article])[0]
    
    #confidance score in 
    if article_prediction == 1:
        article_confidance = round(reliable_probability, 2)
    else:
        article_confidance = round(misleading_probability, 2)


    if article_confidance <= 0.5: #make desision inconclusive if both choices the same
        final = 'Inconclusive'
    else:
        if article_prediction == 0:
            final = 'Misleading'
        elif article_prediction == 1:
            final = 'Reliable'
        else:
            final = 'Inconclusive'
            
    return {
        'content_prediction': article_prediction,
        'confidence': article_confidance,
        'final_decision': final
    }


