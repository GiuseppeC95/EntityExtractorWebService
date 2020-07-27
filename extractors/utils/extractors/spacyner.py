import requests
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *
import numpy as np
import spacy



class SPACYNER(object):
    def __init__(self,):
        self.name = "spacyner"
        self.annotations = None
        self.text = None


    def extract(self, text, lang="en", min_confidence=0.0):
        self.text = text
        self.lang = lang
        nlp = spacy.load(lang)
        doc = nlp(text)

        self.annotations = doc.ents

    def parse(self):
        text = self.text
        annotations = [ann for ann in self.annotations]
        entities = list()
        for ent in annotations:
            obj = {
                'DBtypes': [],
                'types': [ent.label_],
                'start': int(ent.start_char),
                'end': int(ent.end_char)-1,
                'dbpediaUri':'',
                'surface':ent.text,
                'wikidataUri': ''}

            entities.append(obj)
        self.annotations = entities



    def set_annotations(self, annotations):
        self.annotations = annotations

    def get_annotations(self):
        return self.annotations

    def get_text(self):
        return self.text

    def get_info(self):
        return self.recognition, self.disambiguation

    def clear_annotations(self):
        self.annotations = None