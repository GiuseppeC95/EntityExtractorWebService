# Debug time
import time

from extractors.utils.extractors import dandelion, dbspotlight, babelfy, textrazor, meaning_cloud, opencalais, dbspotlight, fox,    spacyner, adel
from extractors.utils.request import *
from extractors.utils.tokenization import *

credentials_apis = json.load(open('extractors/credentials.json'))

credential_index = {key: 0 for key in credentials_apis}

EXTRACTORS = [
    dandelion.DANDELION(credentials_apis['dandelion'][0]),
    babelfy.BABELFY(credentials_apis['babelfy'][0]),
    textrazor.TEXTRAZOR(credentials_apis['textrazor'][0]),
    meaning_cloud.MEANINGCLOUD(credentials_apis['meaning_cloud'][0]),
    opencalais.OPENCALAIS(credentials_apis['opencalais'][0]),
    spacyner.SPACYNER()
]


def getEntities(text, extractors=EXTRACTORS, lang='en', credentials_apis=credentials_apis,
                credential_index=credential_index):
    ensemble_response = {'text': text, 'entities': {}}
    for ext in extractors:
        # Debug
        start_time = time.time()

        flag = True
        count = 0
        while flag:
            try:
                ext.extract(text, lang=lang)
                flag = False
            except Exception as e:
                global ERR
                ERR = e
                # credential_index[ext.name] += 1
                try:
                    print()
                    # ext.change_credendials(credential_index[ext.name])
                except:
                    pass
                count += 1
                if count > 6:
                    raise
                print(ext.name)

        ext.parse()
        ext_entities = ext.get_annotations()
        if type(ext_entities) == dict:
            for key in ext_entities:
                ensemble_response['entities'][ext.name + '___' + key] = ext_entities[key]
        else:
            ensemble_response['entities'][ext.name] = ext_entities

        print("---%s %s seconds ---" % (ext.__class__.__name__, time.time() - start_time))

    return ensemble_response
