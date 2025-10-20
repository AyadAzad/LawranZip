import json
import os

class Translator:
    def __init__(self, translations_dir):
        self.translations_dir = translations_dir
        self.language = 'en'
        self.translations = {}

    def load_language(self, language):
        self.language = language
        file_path = os.path.join(self.translations_dir, f"{language}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            print(f"Translation file for {language} not found.")
            self.translations = {}

    def get(self, key, **kwargs):
        return self.translations.get(key, key).format(**kwargs)
