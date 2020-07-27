import requests
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *
import pandas as pd
import numpy as np


class DBSPOTLIGHT(object):
    def __init__(self, credentials_obj=None,endpoint="api.dbpedia-spotlight.org"):
        self.name = "dbspotlight"
        self.ontology = "wikidata"
        self.endpoint = endpoint
        self.lang = None
        self.annotations = None
        self.text = None
        self.disambiguation = True
        self.recognition = False

    def extract(self, text, extractors="entities,topics", lang="fr", min_confidence=0.0):
        self.lang = lang
        self.text = text
        headers = {
            'Accept': 'application/json',
        }
        params = (
            ('text', text),
            ('confidence', '0.0'),
            ('support', '20'),
        )
        response = requests.get('http://' + self.endpoint + '/' + lang + '/annotate', headers=headers, params=params)
        # print('http://'+self.endpoint+'/'+lang+'/annotate')
        try:
            self.annotations = response.json()["Resources"]
        except:

            print(response.text)
            raise Exception

    def parse(self):
        text = self.text
        annotations = self.annotations
        db_urls = list()
        occurrences = list()
        for ann in annotations:
            occurrences.append({
                'types': [],
                "surface": ann['@surfaceForm'],
                'start':int(ann["@offset"]),
                'end': int(ann["@offset"]) + len(ann['@surfaceForm']),
                "wikidataUri": fromDbpediaToWikidataUri(ann["@URI"]),
                'dbpediaUri':uri,
                'DBtypes': getDbpediaType(uri)
            })

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
