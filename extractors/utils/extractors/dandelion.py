import requests
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *
import pandas as pd
import numpy as np


class DANDELION(object):
    def __init__(self, credentials_obj,endpoint="api.dandelion.eu"):
        self.name = "dandelion"
        self.ontology = "wikidata"
        self.token = credentials_obj
        self.endpoint = endpoint
        self.lang = None
        self.annotations = None
        self.text = None
        self.disambiguation = True
        self.recognition = False

    def extract(self, text, extractors="entities,topics", lang="fr", min_confidence=0.0):
        #FIXME: Se si rimuove la lingua, Dandelion riconosce automaticamente la lingua a partire dal testo
        self.lang = lang
        self.text = text
        ## RIMOSSO param
        params = {"lang": lang, "text": text, "token": self.token, "min_confidence": str(min_confidence)}
        response = requests.post('https://' + self.endpoint + '/datatxt/nex/v1', params=params)
        try:
            self.annotations = response.json()["annotations"]
        except:
            code = response.json()["code"]
            message = response.json()["message"]
            if code == "error.requestURITooLong":
                raise Exception("URI too long")
            elif code == "error.notAllowed" and message == "no units left":
                raise Exception("key expired")
            else:
                raise Exception

    def parse(self):
        text = self.text
        annotations = self.annotations
        wiki_urls = list()
        occurrences = list()
        for ann in annotations:
            wd_uri = fromWikipediaToWikidataUri(ann["uri"])
            db_uri = fromWikidataToDbpediaUri(wd_uri)
            types = getDbpediaType(db_uri)

            obj = {
                'types': [],
                'DBtypes': types,
                'start':ann["start"],
                'end':ann["end"]-1,
                "wikidataUri": wd_uri,
                "dbpediaUri":db_uri
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
        self.token  = credentials_obj