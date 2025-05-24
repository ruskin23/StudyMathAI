import unicodedata

class TextCleaner:
    def normalize_unicode(self, text):
        return unicodedata.normalize('NFKD', text)

    def normalize_whitespace(self, text):
        return text.replace('\u00A0', ' ').replace('\u200B', '')

    def normalize_punctuation(self, text):
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")
        text = text.replace("–", "-").replace("—", "-")
        return text

    def clean(self, text):
        text = self.normalize_unicode(text)
        text = self.normalize_whitespace(text)
        text = self.normalize_punctuation(text)
        return text.lower()
