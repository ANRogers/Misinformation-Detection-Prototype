import re
import html
import nltk

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('wordnet')
# nltk.download('omw-1.4')  

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

STOPWORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    # remove HTML components
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    
    # remove non-words and extra spaces
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    text = text.lower()

    # tokenize
    words = nltk.word_tokenize(text)

    # remove stopwords and lemmatize
    cleaned_words = []
    for word in words:
        if word not in STOPWORDS and len(word) > 2: 
            lemma = lemmatizer.lemmatize(word)
            cleaned_words.append(lemma)

    return ' '.join(cleaned_words) #recombine text and return
