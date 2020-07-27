import requests
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *
import numpy as np


class OPENCALAIS(object):
    def __init__(self,credentials_obj, endpoint="api.thomsonreuters.com"):
        self.name = "opencalais"
        self.ontology = "opencalais"
        self.access_token = credentials_obj
        self.endpoint = endpoint
        self.lang = None
        self.annotations = None
        self.text = None
        self.headers = {'X-AG-Access-Token': self.access_token, 'Content-Type': 'text/raw',
                        'outputformat': 'application/json'}
        self.disambiguation = False
        self.recognition = True

    def extract(self, text, lang="fr", min_confidence=0.0):
        self.lang = lang
        self.text = text
        files = {'file': text}
        response = requests.post('https://' + self.endpoint + '/permid/calais', files=files, headers=self.headers,
                                 timeout=80)
        obj = response.json()
        entities = [obj[key] for key in obj if key != 'doc']
        self.annotations = entities

    def parse(self):
        text = self.text
        annotations = [ann for ann in self.annotations if 'instances' in ann]
        opencalais_annotations = list()
        for ann in annotations:
            occurrences = ann['instances']
            for o in occurrences:
                start = o['offset'] - 100
                end = o['offset'] - 100 + o['length']


                obj = {
                    'DBtypes': [],
                    'types': [ann["_type"]],
                    'start': start,
                    'end': end,
                    'dbpediaUri':'',
                    'wikidataUri': ''}
                obj['surface'] = self.text[obj['start']:obj['end']+1]
                opencalais_annotations.append(obj)
        self.annotations = opencalais_annotations



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