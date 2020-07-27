import numpy as np
from foxpy.fox import *
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *




class FOX(object):
    def __init__(self):
        self.name = "fox"
        self.ontology_uri = "wikidata"
        self.ontology_type = "dbpedia"
        self.lang = None
        self.text = None
        self.annotations = None
        self.disambiguation = True
        self.recognition = True

    def extract(self, text, extractors="entities,topics", lang="en", min_confidence=0.0):
        self.lang = lang
        self.text = text

        m = Fox()
        resp = m.recognizeText( text)
        if '@graph' in resp:
            self.annotations = resp['@graph']
        else:
            self.annotations =  []

    def parse(self):
        text = self.text
        annotations = self.annotations
        occurrences = list()
        for ann in annotations:
            if 'taClassRef' in ann or 'taIdentRef' in ann:
                if 'taClassRef' in ann:
                    types = [t for t in ann['taClassRef'] if 'dbo' in t]
                else:
                    types = []

                if 'taIdentRef' in ann and 'dbr' in ann['taIdentRef']:
                    db_uri = ann['taIdentRef'].replace('dbr','http://dbpedia.org/resource/')
                    wd_uri = fromDbpediaToWikidataUri(db_uri)
                else:
                    db_uri = ''
                    wd_uri = ''

                obj = {
                    'types': [],
                    'start': int(ann['beginIndex']),
                    'end': int(ann['endIndex'])-1,
                    'wikidataUri': wd_uri,
                    'dbpediaUri':db_uri,
                    'DBtypes': types
                    }
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
        self.api_key = credentials_obj