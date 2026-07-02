#backend/app/preprocessing/traditional_engine.py
import re

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

from .base import PreprocessingEngine
from .config import PreprocessingConfig
from .processed_document import ProcessedDocument


STOPWORDS = set(stopwords.words("english"))

stemmer = PorterStemmer()

lemmatizer = WordNetLemmatizer()

class TraditionalPreprocessingEngine(PreprocessingEngine):

    def __init__(self, config):

        self.config = config


    def process(self, text):

        tokens = re.findall(r"\w+", text)

        processed = []

        for token in tokens:

            if self.config.lowercase:
                token = token.lower()

            if self.config.remove_stopwords:

                if token in STOPWORDS:
                    continue

            if self.config.use_stemming:

                token = stemmer.stem(token)

            elif self.config.use_lemma:

                token = lemmatizer.lemmatize(token)

            processed.append(token)

        return ProcessedDocument(terms=processed)