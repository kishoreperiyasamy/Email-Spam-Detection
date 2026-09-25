import re
import string

# Robust English stopwords list (does not require external network download at runtime)
STANDARD_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

try:
    import nltk
    from nltk.corpus import stopwords
    try:
        NLTK_STOPWORDS = set(stopwords.words('english'))
        STOPWORDS = STANDARD_STOPWORDS.union(NLTK_STOPWORDS)
    except Exception:
        STOPWORDS = STANDARD_STOPWORDS
except Exception:
    STOPWORDS = STANDARD_STOPWORDS

def extract_text_statistics(text: str) -> dict:
    """
    Extracts surface-level statistical indicators before aggressive cleaning:
    - Capital letter ratio
    - Exclamation mark count
    - Dollar sign count
    - Question mark count
    - Total character and word length
    """
    if not text:
        return {
            "total_chars": 0,
            "total_words": 0,
            "caps_count": 0,
            "caps_ratio": 0.0,
            "exclamation_count": 0,
            "dollar_count": 0,
            "question_count": 0,
            "punctuation_count": 0,
            "punctuation_ratio": 0.0
        }

    total_chars = len(text)
    words = text.split()
    total_words = len(words)
    
    caps_count = sum(1 for c in text if c.isupper())
    caps_ratio = round((caps_count / max(total_chars, 1)) * 100, 2)
    
    exclamation_count = text.count('!')
    dollar_count = text.count('$') + text.count('€') + text.count('£')
    question_count = text.count('?')
    
    punct_count = sum(1 for c in text if c in string.punctuation)
    punct_ratio = round((punct_count / max(total_chars, 1)) * 100, 2)
    
    return {
        "total_chars": total_chars,
        "total_words": total_words,
        "caps_count": caps_count,
        "caps_ratio": caps_ratio,
        "exclamation_count": exclamation_count,
        "dollar_count": dollar_count,
        "question_count": question_count,
        "punctuation_count": punct_count,
        "punctuation_ratio": punct_ratio
    }

def clean_email_text(text: str) -> str:
    """
    Cleans raw email text (subject + body) for TF-IDF vectorization:
    - Strips HTML tags
    - Converts to lowercase
    - Normalizes URLs and emails to placeholder tokens
    - Strips non-alphanumeric chars (retaining spaces)
    - Removes stopwords
    - Normalizes whitespace
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Remove HTML tags
    clean = re.sub(r'<[^>]+>', ' ', text)
    
    # 2. Normalize URLs to 'urltoken'
    clean = re.sub(r'https?://\S+|www\.\S+', ' urltoken ', clean, flags=re.IGNORECASE)
    
    # 3. Normalize email addresses to 'emailtoken'
    clean = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' emailtoken ', clean)
    
    # 4. Normalize monetary amounts to 'moneytoken'
    clean = re.sub(r'[$€£]\s?\d+(?:,\d{3})*(?:\.\d+)?|\b\d+\s?(?:dollars|usd|eur|gbp)\b', ' moneytoken ', clean, flags=re.IGNORECASE)

    # 5. Convert to lowercase
    clean = clean.lower()

    # 6. Remove numbers and punctuation, keep words
    clean = re.sub(r'[^a-z\s]', ' ', clean)

    # 7. Tokenize and remove stopwords
    tokens = clean.split()
    filtered_tokens = [tok for tok in tokens if tok not in STOPWORDS and len(tok) > 2]

    return " ".join(filtered_tokens)
