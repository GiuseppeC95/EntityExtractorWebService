from igraph import *
import numpy as np
import pickle
import json
from utils.request import *
from utils.metrics import *
from utils.tokenization import *
from itertools import combinations
from langdetect import detect
import time
import spacy
from polyglot.tag import get_pos_tagger, get_transfer_pos_tagger, get_ner_tagger



def fromTokensToPOS(tokens,lang='en'):
    tagger_ = get_pos_tagger(lang='en')
    nlp = spacy.load('en')
    doc = nlp.tokenizer.tokens_from_list(tokens)
    tags= nlp.tagger(doc)
    pos = list()
    for i,k in enumerate(tagger_.annotate(tokens)):
        pos.append([k[1],tags[i].pos_])
    return pos


EMBEDDING_DATA_PATH = 'data/embedding_data/'


def getGraphNodes_and_Properties():
    embdedding_specifications_dict = json.load(open(EMBEDDING_DATA_PATH + 'embedding_specifications.json'))
    graph_path = embdedding_specifications_dict['structural']
    graph_obj = pickle.load(open(graph_path, 'rb'))
    MAX_DISTANCE_NODES = graph_obj['max_distance']
    structural_graph = graph_obj['graph']
    properties_list = embdedding_specifications_dict['semantic']
    return structural_graph, properties_list, MAX_DISTANCE_NODES


structural_graph, properties_list, MAX_DISTANCE_NODES = getGraphNodes_and_Properties()

def getProperties(properties_list=properties_list):
    #TODO
    return ['struct','label','description','occupation']

def getTypeFeatures(type_list,types=None):
    if type(type_list[0]) == str:
        type_list = [[t] for t in type_list]

    if not types:
        types = sorted(list(set([item for sublist in type_list for item in sublist])))


    one_hot_types = [[int(t in item) for t in types] for item in type_list]

    return one_hot_types, types


def getDistanceNodes(wd_id_1, wd_id_2, structural_graph):
    virtuals = 0
    try:
        n1 = VIRTUAL_NODES[n1]
        virtuals += 1
    except:
        n1 = wd_id_1
    try:
        n2 = VIRTUAL_NODES[n2]
        virtuals += 1
    except:
        n2 = wd_id_2
    if virtuals == 2:
        if wd_id_1 != wd_id_2:
            dist = 2
        else:
            dist = 0
    else:
        dist = structural_graph.shortest_paths(n1, n2)[0][0] + virtuals
    return dist


def getStructSimilarity(wd_id_1, wd_id_2, structural_graph=structural_graph, MAX_DISTANCE_NODES=MAX_DISTANCE_NODES):
    if type(wd_id_1) != str or type(wd_id_2) != str:
        return 0.0
    else:
        try:
            d_struct = min([1.0, getDistanceNodes(wd_id_1, wd_id_2, structural_graph) / MAX_DISTANCE_NODES])
        except:
            return 0.0
        sim_struct = abs(1.0 - d_struct)
        return sim_struct


def assignMetric(s):
    if s == "one-hot":
        return oneHotSimilarity
    elif s == 'fuzzy':
        return fuzzSimilarity
    elif s == 'tf-idf':
        return ffIdfSimilarity


def getLabelsFeaturesToken(labels, metric=fuzzSimilarity):
    label_features = []
    for t in combinations(labels, 2):
        l1, l2 = t
        label_features.append(metric(l1, l2))
    return label_features


def getSematicSimilarity(wd_id_1, wd_id_2, properties, lang):
    semantic_similarity_array = []
    if not wd_id_1 or not wd_id_2:
        return [0.0 for p in properties]
    for p in properties:
        if 'filter' in p:
            items_1 = set()
            items_2 = set()
            if lang in p['filter']:
                items_1 = items_1 | set(wikiQuery(wd_id_1, p['property'], filter_q=p['filter'][lang])['o'])
                items_2 = items_2 | set(wikiQuery(wd_id_2, p['property'], filter_q=p['filter'][lang])['o'])
        else:
            items_1 = set(wikiQuery(wd_id_1, p['property'])['o'])
            items_2 = set(wikiQuery(wd_id_2, p['property'])['o'])
        sim_func = assignMetric(p['metric'])
        similarities = [sim_func(i1, i2) for i2 in items_2 for i1 in items_1]
        if len(similarities) != 0:
            semantic_similarity_array.append(max(similarities))
        else:
            semantic_similarity_array.append(0.0)
    return semantic_similarity_array


def getUrisSimilarityVector(wd_id_1, wd_id_2, G=structural_graph, properties_list=properties_list,
                            MAX_DISTANCE_NODES=MAX_DISTANCE_NODES, lang='fr'):
    if type(wd_id_1) == str and type(wd_id_2) == str:
        sim_struct = getStructSimilarity(wd_id_1, wd_id_2, structural_graph, MAX_DISTANCE_NODES)
        sim_semantic = getSematicSimilarity(wd_id_1, wd_id_2, properties_list, lang)
        return np.array([sim_struct] + sim_semantic)
    else:
        return np.zeros(len(properties_list) + 1)


def getEntityFeatures(entity_list_dict, ontology_entity_dict, lang):
    PRECOMPUTED_SIM = {}
    extractors_uris = list(entity_list_dict.keys())
    com_ext = [sorted(item) for item in list(combinations(extractors_uris, 2))] + [(ext, ext) for ext in
                                                                                   extractors_uris]

    entity_features = {ext1: {ext2: [] for ext2 in extractors_uris} for ext1 in extractors_uris}
    entity_MATRIX = dict()

    length_list = len(entity_list_dict[extractors_uris[0]])
    for k in range(length_list):
        for comb in com_ext:
            uri1, uri2 = entity_list_dict[comb[0]][k], entity_list_dict[comb[1]][k]
            if not bool(uri1):
                uri1 = np.NAN
            if not bool(uri2):
                uri2 = np.NAN

            key = str(uri1) + '_' + str(uri2) + '_' + lang
            try:
                sim = PRECOMPUTED_SIM[key]
            except:
                sim = list(getUrisSimilarityVector(uri1, uri2, lang=lang)) + [
                    int(type(uri1) == type(uri2) == float or uri1 == uri2)]
                PRECOMPUTED_SIM[key] = sim
            if (uri1, uri2) not in entity_MATRIX:
                entity_MATRIX[(uri1, uri2)] = sim
            if (uri2, uri1) not in entity_MATRIX:
                entity_MATRIX[(uri2, uri1)] = sim
            entity_features[comb[0]][comb[1]].append(sim)
            if comb[0] != comb[1]:
                entity_features[comb[1]][comb[0]].append(sim)

    for ext in entity_features:
        for z, key in enumerate(extractors_uris):
            if z != 0:
                X_ext = np.append(X_ext, entity_features[ext][key], axis=1)
            else:
                X_ext = np.array(entity_features[ext][key])
        entity_features[ext] = X_ext
    return entity_features, entity_MATRIX


def fromOntologyEdglist_to_ClassRapresentation_notexclusive(edgelist_pd, set_root, limit):
    classes_rapresentation_dict = dict()
    roots = deepcopy(set_root)
    total_len_rapresentation = 0
    flag = False
    while len(classes_rapresentation_dict) != limit:
        df = edgelist_pd[edgelist_pd["class"].isin(roots)]
        roots = set(df['subclass'])
        len_rapresentation = len(roots)
        for i, r in enumerate(roots):
            past_features = []
            if flag:
                to_add_list = [classes_rapresentation_dict[c] for c in set(df[df['subclass'] == r]['class'])]
                for to_add in to_add_list:
                    if len(past_features) != 0:
                        past_features = [x + y for x, y in zip(past_features, to_add)]
                    else:
                        past_features = to_add
            classes_rapresentation_dict[r] = past_features + [int(i == j) for j in range(len_rapresentation)]
        flag = True

        for cl in (set(classes_rapresentation_dict.keys()) - roots):
            classes_rapresentation_dict[cl] += [0 for i in range(len_rapresentation)]
    return classes_rapresentation_dict


def fromOntologyEdglist_to_ClassRapresentation(edgelist_pd):
    subclasses = set(edgelist_pd["subclass"])
    classes = set(edgelist_pd["class"])
    set_root = classes - subclasses
    if len(set_root) != 1:
        for r in set_root:
            edgelist_pd = edgelist_pd.append([{
                "class": "_root_",
                "subclass": r
            }]
                , ignore_index=True)
        subclasses = set(edgelist_pd["subclass"])
        classes = set(edgelist_pd["class"])
        set_root = classes - subclasses
    return fromOntologyEdglist_to_ClassRapresentation_notexclusive(edgelist_pd, set_root, len(classes | subclasses) - 1)

