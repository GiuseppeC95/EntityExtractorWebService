import numpy as np
import textrazor
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *




class TEXTRAZOR(object):
    def __init__(self,credentials_obj, endpoint="api.textrazor.com"):
        self.name = "textrazor"
        self.ontology_uri = "wikidata"
        self.ontology_type = "dbpedia"
        self.api_key = credentials_obj
        self.lang = None
        self.text = None
        self.annotations = None
        self.disambiguation = True
        self.recognition = True

    def extract(self, text, extractors="entities,topics", lang="fr", min_confidence=0.0):
        self.lang = lang
        self.text = text
        lang = lang.replace("fr", "fre").replace("en", "eng").replace('it','ita')
        textrazor.api_key = self.api_key
        client = textrazor.TextRazor(extractors=["entities"])
        client.set_language_override(lang)
        try:
            response = client.analyze(text)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if "daily TextRazor request limit" in str(exc_value):
                raise Exception("key expired")
            else:
                raise Exception
        entities = [entity.json for entity in response.entities()]
        self.annotations = entities

    def parse(self):
        text = self.text
        annotations = self.annotations
        occurrences = list()
        for ann in annotations:
            if 'wikidataId' in ann:
                id_ = ann['wikidataId']
                db_uri = fromWikidataToDbpediaUri('http://www.wikidata.org/entity/'+id_)
                types = getDbpediaType(db_uri)
                obj = {
                    'types': [],
                    'start': int(ann['startingPos']),
                    'end': int(ann['endingPos'])-1,
                    'wikidataUri': 'http://www.wikidata.org/entity/'+id_,
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