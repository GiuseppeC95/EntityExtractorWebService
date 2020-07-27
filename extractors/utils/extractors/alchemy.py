from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions

from utils.parsing import *
from utils.request import *
from utils.tokenization import *
import re
import numpy as np


class ALCHEMY(object):
    def __init__(self):
        self.name = "alchemy"
        self.ontology = "alchemy"
        credentials_obj = get_credentials(self.name)
        self.credentials = NaturalLanguageUnderstandingV1(
            username=credentials_obj["username"],
            password=credentials_obj["password"],
            version="2017-02-27"
        )
        self.lang = None
        self.text = None
        self.annotations = None
        self.disambiguation = False
        self.recognition = True

    def extract(self, text, extractors="entities,topics", lang="fr", min_confidence=0.0):
        natural_language_understanding = self.credentials
        self.lang = lang
        self.text = text
        response = natural_language_understanding.analyze(
            text=text, language=lang,
            features=Features(entities=EntitiesOptions(limit=250))
        )
        annotations = response["entities"]
        self.annotations = annotations

    def parse(self):
        text = self.text
        annotations = self.annotations
        occurrences = list()
        for ann in annotations:
            matched = list(re.finditer(r"\b" + re.escape(ann['text']) + '\W', text))
            for a in matched:
                obj = {
                    'DBtypes': [],
                    'types': [ann['type']],
                    'start': a.start(),
                    'end': a.end() - 1,
                    'dbpediaUri':'',
                    'wikidataUri': ''}
                obj['surface'] = self.text[obj['start']:obj['end']+1]
                occurrences.append(obj)
        self.annotations = occurrences


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