import requests
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *
import numpy as np


class MEANINGCLOUD(object):
    def __init__(self,credentials_obj, endpoint="api.meaningcloud.com"):
        self.name = "meaning_cloud"
        self.ontology = "meaning_cloud"
        self.api_key = credentials_obj
        self.endpoint = endpoint
        self.lang = None
        self.annotations = None
        self.text = None
        self.disambiguation = False
        self.recognition = True

    def extract(self, text, extractors="entities,topics", lang="fr", min_confidence=0.0):
        self.lang = lang
        self.text = text
        params = (
            ('key', self.api_key),
            ('of', 'json'),
            ('lang', lang),
            ('txt', text),
            ('tt', 'a')
        )
        response = requests.post('https://api.meaningcloud.com/topics-2.0', params=params)
        self.annotations = response.json()["entity_list"]

    def parse(self):
        text = self.text
        annotations = self.annotations
        occurrences = list()
        for ann in annotations:
            type_ = ann["sementity"]['type'].split('>')[-1]
            if type_ != 'Top':
                for inst in ann["variant_list"]:
                    obj = {
                        'DBtypes': [],
                        'types': [ann["sementity"]['type'].split('>')[-1]],
                        'start': int(inst['inip']),
                        'end': int(inst['endp']) + 1,
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


    def change_credendials(self,credentials_obj):
        self.token  = credentials_obj