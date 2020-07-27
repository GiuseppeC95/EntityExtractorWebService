import requests
import numpy as np
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *
import unicodedata


def removeAccents(s):
    s = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    s = s.replace('–', '-')
    return s


class ADEL(object):
    def __init__(self, endpoint="adel.eurecom.fr"):
        self.name = "adel"
        self.ontology = "adel"
        self.endpoint = endpoint
        self.lang = None
        self.annotations = None
        self.text = None
        self.disambiguation = False
        self.recognition = True

    def extract(self, text, extractors="entities,topics", lang="en", min_confidence=0.0):
        self.lang = lang
        self.text = text
        headers = {
            'accept': 'text/plain;charset=utf-8',
            'content-type': 'application/json;charset=utf-8',
        }

        text = removeAccents(text)
        self.annotations = dict()

        adelmodels = ['default', 'aida', 'oke2015', 'oke2016', 'oke20171', 'oke20172', 'oke20173', 'neel2014', 'neel2015', 'neel2016']

        for m in adelmodels:
            params = (
                ('setting', m),
                ('lang', lang)
            )
            data = '{ "content": "' + text.replace('"', '\\"') + '", "input": "raw", "output": "brat"}'
            try:
                response = requests.post('http://' + self.endpoint + '/v1/extract', headers=headers, params=params,
                                         data=data)
                self.annotations[m] = response.text

            except:
                pass

    def parse(self):
        text = self.text
        annotations = self.annotations
        entities = dict()
        for m in annotations:
            entities[m] = list()
            string = self.annotations[m]
            annotations_dict = dict()
            lines = string.splitlines()
            for l in lines:
                split_1 = l.split('\t')
                if len(l) > 0:
                    if l[0] == 'T':
                        annotation_key = split_1[0]
                        annotation_text = split_1[-1]
                        try:
                            split_2 = split_1[1].split(' ')
                        except:
                            print(l.split_1)
                            raise Exception
                        start_char = int(split_2[1])
                        end_char = int(split_2[-1])+1
                        category = split_2[0].split('#')[-1]
                        obj = {
                            'types': category,
                            'start': start_char,
                            'end': end_char,
                            'wikidataUri': '',
                            'dbpediaUri':'',
                            'DBtypes': []
                            }
                        entities[m].append(obj)
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



