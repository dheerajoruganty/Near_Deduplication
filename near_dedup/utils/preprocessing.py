import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

# Load English stop words
STOP_WORDS = set(stopwords.words("english"))


def clean_text(text):
    """Remove punctuation, convert to lowercase, and strip whitespace.

    Parameters:
        text (str): Input text to clean.

    Returns:
        str: Cleaned text.
    """
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = text.strip()  # Remove leading/trailing whitespace
    return text


def remove_stopwords(text):
    """Remove common stop words from text.

    Parameters:
        text (str): Input text.

    Returns:
        str: Text without stop words.
    """
    tokens = word_tokenize(text)  # Tokenize text
    filtered_tokens = [word for word in tokens if word not in STOP_WORDS]
    return " ".join(filtered_tokens)


def preprocess_text(text, remove_stopwords_flag=True):
    """Perform full preprocessing on text: clean, and optionally remove stopwords.

    Parameters:
        text (str): Input text.
        remove_stopwords_flag (bool): If True, remove stop words.

    Returns:
        str: Fully preprocessed text.
    """
    text = clean_text(text)
    if remove_stopwords_flag:
        text = remove_stopwords(text)
    return text


def generate_ngrams(text, n=3):
    """Generate n-grams from the input text.

    Parameters:
        text (str): Input text.
        n (int): N-gram size (default is 3).

    Returns:
        list: List of n-grams as tuples.
    """
    tokens = word_tokenize(text)  # Tokenize text
    return list(ngrams(tokens, n))


def tokenize_to_set(text):
    """Tokenize text into a set of unique words.

    Parameters:
        text (str): Input text.

    Returns:
        set: Set of unique tokens.
    """
    tokens = word_tokenize(text)
    return set(tokens)
