class Normalizer:
    def __init__(self):
        self.nlp = None

    def init_spacy(self):
        import ru_core_news_md
        self.nlp = ru_core_news_md.load()


    def normalize(self, text):
        if self.nlp is None:
            self.init_spacy()
        normalized_text = []
        doc = self.nlp(text)
        for token in doc:
            lemma = token.lemma_
            if lemma:
                normalized_text.append(lemma)
            else:
                normalized_text.append(token.text)
        return " ".join(normalized_text)


if __name__ == "__main__":
    normalizer = Normalizer()
    print(normalizer.normalize("ивана иванова"))
