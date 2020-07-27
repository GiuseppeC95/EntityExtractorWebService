import urllib.request, urllib.parse, urllib.error
import json
from extractors.utils.parsing import *
from extractors.utils.request import *
from extractors.utils.tokenization import *
import pandas as pd
import numpy as np


class BabelfyJSONKeys(object):
    TOKEN_FRAGMENT = "tokenFragment"
    CHAR_FRAGMENT = "charFragment"
    CHAR_FRAGMENT_START = "start"
    CHAR_FRAGMENT_END = "end"
    BABEL_SYNSET_ID = "babelSynsetID"
    DBPEDIA_URL = "DBpediaURL"
    BABELNET_URL = "BabelNetURL"
    SCORE = "score"
    COHERENCE_SCORE = "coherenceScore"
    GLOBAL_SCORE = "globalScore"
    SOURCE = "source"


class AnnTypeValues(object):
    ALL = "ALL"  # Disambiguates all
    CONCEPTS = "CONCEPTS"  # Disambiguates concepts only
    NAMED_ENTITIES = "NAMED_ENTITIES"  # Disambiguates named entities only


class AnnResValues(object):
    BN = "BN"  # Annotate with BabelNet synsets
    WIKI = "WIKI"  # Annotate with Wikipedia page titles
    WN = "WN"  # Annotate with WordNet synsets


class MatchValues(object):
    EXACT_MATCHING = "EXACT_MATCHING"  # Only exact matches are considered for disambiguation
    PARTIAL_MATCHING = "PARTIAL_MATCHING"  # Both exact and partial matches (e.g.


class MCSValues(object):
    OFF = "OFF"  # Do not use Most Common Sense
    ON = "ON"  # Use Most Common Sense
    ON_WITH_STOPWORDS = "ON_WITH_STOPWORDS"  # Use Most Common Sense even on Stopwords


class CandsValues(object):
    ALL = "ALL"  # Return all candidates for a fragment.
    TOP = "TOP"  # Return only the top ranked candidate for a fragment.


class PosTagValues(object):
    # Tokenize the input string by splitting all characters as single tokens
    # (all tagged as nouns, so that we can disambiguate nouns).
    CHAR_BASED_TOKENIZATION_ALL_NOUN = "CHAR_BASED_TOKENIZATION_ALL_NOUN"
    INPUT_FRAGMENTS_AS_NOUNS = "INPUT_FRAGMENTS_AS_NOUNS"  # Interprets input fragment words as nouns.
    NOMINALIZE_ADJECTIVES = "NOMINALIZE_ADJECTIVES"  # Interprets all adjectives as nouns.
    STANDARD = "STANDARD"  # Standard PoS tagging process.


class SemanticAnnotation(object):

    def __init__(self, babelfy_dict):
        self.babelfy_dict = babelfy_dict

    def babelfy_dict(self):
        return self.babelfy_dict

    def token_fragment(self):
        return self.babelfy_dict[BabelfyJSONKeys.TOKEN_FRAGMENT]

    def char_fragment(self):
        return self.babelfy_dict[BabelfyJSONKeys.CHAR_FRAGMENT]

    def char_fragment_start(self):
        return self.char_fragment()[BabelfyJSONKeys.CHAR_FRAGMENT_START]

    def char_fragment_end(self):
        return self.char_fragment()[BabelfyJSONKeys.CHAR_FRAGMENT_END]

    def babel_synset_id(self):
        return self.babelfy_dict[BabelfyJSONKeys.BABEL_SYNSET_ID]

    def dbpedia_url(self):
        return self.babelfy_dict[BabelfyJSONKeys.DBPEDIA_URL]

    def babelnet_url(self):
        return self.babelfy_dict[BabelfyJSONKeys.BABELNET_URL]

    def coherence_score(self):
        return self.babelfy_dict[BabelfyJSONKeys.COHERENCE_SCORE]

    def global_score(self):
        return self.babelfy_dict[BabelfyJSONKeys.GLOBAL_SCORE]

    def source(self):
        return self.babelfy_dict[BabelfyJSONKeys.SOURCE]

    def postag(self):
        return self.babel_synset_id()[-1]

    def pprint(self):
        print(self.babel_synset_id())
        print(self.babelnet_url())
        print(self.dbpedia_url())
        print(self.source())


class BABELFY(object):
    TEXT = "text"
    LANG = "lang"
    KEY = "key"
    ANNTYPE = "annType"
    ANNRES = "annRes"
    TH = "th"
    MATCH = "match"
    MCS = "MCS"
    DENS = "dens"
    CANDS = "cands"
    POSTAG = "postag"
    EXTAIDA = "extAIDA"

    PARAMETERS = [TEXT, LANG, KEY, ANNTYPE, ANNRES, TH, MATCH, MCS, DENS, CANDS, POSTAG, EXTAIDA]

    API = "https://babelfy.io/v1/"
    DISAMBIGUATE = "disambiguate?"

    def __init__(self,credentials_obj):
        self.name = "babelfy"
        self.ontology = "wikidata"
        self.key = credentials_obj
        self.lang = None
        self.annotations = None
        self.text = None
        self.disambiguation = True
        self.recognition = False

    def extract(self, text, lang="fr", min_confidence=0.0, anntype=None, annres=None, th=None,
                match=None, mcs=None, dens=None, cands=None, postag=None,
                extaida=None):

        self.lang = lang
        self.text = text
        key = self.key

        values = [text, lang.upper(), key, anntype, annres, th, match, mcs, dens,
                  cands, postag, extaida]

        query = urllib.parse.urlencode({param: value for param, value in zip(self.PARAMETERS, values)
                                        if value is not None})

        json_string = urllib.request.urlopen(self.API + self.DISAMBIGUATE + query).read().decode("utf-8")
        # print json_string
        babelfy_jsons = json.loads(json_string)
        if 'message' in babelfy_jsons:
            if 'daily requests limit' in babelfy_jsons['message']:
                raise Exception("key expired")
        semantic_annotations = [SemanticAnnotation(babelfy_json) for babelfy_json in babelfy_jsons]
        entities = [s.babelfy_dict for s in semantic_annotations]
        self.annotations = entities

    def parse(self):
        text = self.text
        annotations = self.annotations
        occurrences = list()
        for ann in annotations:
            start = ann['charFragment']['start']
            end = ann['charFragment']['end']
            uri = ann["DBpediaURL"]
            if uri != '':
                w_uri = fromDbpediaToWikidataUri(uri)
                types = getDbpediaType(uri)

                obj = {
                'types': [],
                    'DBtypes': types,
                    'start': start,
                    'end': end,
                    'dbpediaUri':uri,
                    'wikidataUri': w_uri}
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
        self.key = credentials_obj

