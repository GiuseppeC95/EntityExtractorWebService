import re
import urllib
import json
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF, CSV, TSV
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
import wikipediaapi

Q_DB_WD_SAMEAS = '''
select ?wd_uri
where{
<STR_TO_SUB> <http://www.w3.org/2002/07/owl#sameAs> ?wd_uri.
filter(contains(str(?wd_uri), "www.wikidata.org"))
}
'''

Q_WD_DB_SAMEAS = '''
select ?wd_uri ?db_uri
where{
values ?wd_uri { <STR_TO_SUB> }
?db_uri <http://www.w3.org/2002/07/owl#sameAs> ?wd_uri.
}
'''

q_db_type = '''
select ?db_uri ?o
where{
values ?db_uri { <STR_TO_SUB> }
?db_uri rdf:type ?o.
filter(contains(str(?o),"dbpedia.org/ontology"))
}
'''

DB_WIKI_ISPRIMARYTOPIC = '''
select ?db_fr_uri ?wiki_uri
where{
values ?db_fr_uri { <STR_TO_SUB> }
?db_fr_uri foaf:isPrimaryTopicOf ?wiki_uri.
}
'''

DB_WIKI_ISDISAMBIGUATION = '''
select ?db_uri
where{
<STR_TO_SUB> <http://dbpedia.org/ontology/wikiPageRedirects> ?db_uri.
}
'''

DBLANG_DB_SAMEAS = '''
select ?db_uri
where{
<STR_TO_SUB> owl:sameAs ?db_uri.
filter(contains(str(?db_uri), "http://<LANG>dbpedia.org"))
}
'''

WD_NEIGHBOURS_ENTITIES = '''
select ?s ?o
where{
values ?s { <STR_TO_SUB> }
?s ?p ?o.
filter(contains(str(?o), "http://www.wikidata.org/entity/Q"))
}
'''

Q_DB_TYPE = '''
select ?db_uri ?o
where{
values ?db_uri { <STR_TO_SUB> }
?db_uri rdf:type ?o.
filter(contains(str(?o),"dbpedia.org/ontology"))
}
'''

qd_query = '''
select distinct *
where{
    values ?s { <STR_TO_SUB> }
    ?s ?p ?o
    <FILTER>
}
'''
def getRequestURL(query, endpointURL='http://fr.dbpedia.org/sparql', q=False):
    escapedQuery = urllib.parse.quote(query)
    requestURL = endpointURL + "?query=" + escapedQuery + "&output=text/csv&timeout=10000000"
    if q:
        return requestURL, query
    else:
        return requestURL

def getRequestResult(requestURL):
    request = urllib.request.Request(requestURL)
    result = urllib.request.urlopen(request)
    return result


def getRequestResult_and_Read(requestURL):
    result = getRequestResult(requestURL)
    text = result.read().decode("utf-8")
    return text


def fromXMLtoDataFrame(sstr):
    obj_list = list()
    rex_column_names = re.compile(r"<variable name='(.*?)'")
    column_names = re.findall(rex_column_names, sstr)
    rex = re.compile(r'<result.*?>(.*?)</result>', re.S | re.M)
    results = re.findall(rex, sstr)
    flag = False
    for j, res in enumerate(results):
        obj = {}
        if flag:
            print(j)
            flag = False
        for c in column_names:
            rex = re.compile(r"<binding name='" + c + "'>\n\t\t\t\t<.*?>(.*?)</.*?>\n\t\t\t</binding>", re.S | re.M)
            obj[c] = re.findall(rex, res)[0]
        try:
            obj_list.append(obj)
        except:
            print(results)
            print("No item")
            print(rex_3)
            raise Exception
            flag = True
    if len(obj_list) > 0:
        return pd.DataFrame(obj_list)
    else:
        return pd.DataFrame(data=[], columns=column_names)


def wikiQuery(s, p, filter_q='', q=qd_query):
    if s[0] == 'Q':
        s = 'http://www.wikidata.org/entity/' + s
    q = q.replace('STR_TO_SUB', s).replace('?p', p).replace('<FILTER>', filter_q)
    URL = getRequestURL(q, endpointURL='https://query.wikidata.org/sparql')
    try:
        text = getRequestResult_and_Read(URL)
    except:
        text = getRequestResult_and_Read(URL)
    df = fromXMLtoDataFrame(text)
    return df


def isEnglishDbpediaUri(uri):
    return "http://dbpedia.org" in uri

def detectEndpoint(uri):
    if 'dbpedia.org' in uri:
        match = re.match("http://(.*)dbpedia.org",uri)
        endpoint = match.group(0)+'/sparql'
    elif 'wikidata.org' in uri:
        endpoint = 'https://query.wikidata.org/sparql'
    else:
        print('No endpoint',uri)
        return ''
    return endpoint



def getSPARQLResponse(query,endpoint,timeout=None):
    #print(endpoint,query)
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    if bool(timeout):
        sparql.setTimeout(timeout)
    if '//dbpedia' in endpoint:
        sparql.setReturnFormat(CSV)
        results = sparql.query().convert()
        df = pd.read_csv(StringIO(results.decode('utf-8')))
    else:
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        columns = results['head']['vars']
        records_response = results['results']['bindings']
        if len(records_response) == 0:
            df = pd.DataFrame()
        else:
            df = pd.DataFrame([{key:r[key]['value'] for key in r} for r in records_response])
            df = df[columns]
    return df


    

def fromDbpediaToDbpediaUri(db_uri,lang='en'):
    if lang == 'en':
        lang = ''
    else:
        lang += '.'
    query = DBLANG_DB_SAMEAS.replace('STR_TO_SUB',db_uri).replace('<LANG>',lang)
    endpoint = detectEndpoint(db_uri)
    df = getSPARQLResponse(query,endpoint)
    if len(df) > 0:
        col = df.columns[1]
        db_uri = df[col][0]
        return db_uri
    else:
        return ''

def fromDbpediaToWikidataUri(db_uri):
    query = DB_WIKI_ISDISAMBIGUATION.replace('STR_TO_SUB',db_uri)
    endpoint = detectEndpoint(db_uri)
    df_mapping_db_wd = getSPARQLResponse(query,endpoint)
    if len(df_mapping_db_wd) > 0:
        col = df_mapping_db_wd.columns[-1]
        db_uri = df_mapping_db_wd[col][0]

    query = Q_DB_WD_SAMEAS.replace('STR_TO_SUB',db_uri)
    df_disambiguation = getSPARQLResponse(query,endpoint)
    if len(df_disambiguation) > 0:
        col = df_disambiguation.columns[-1]
        wd_uri = df_disambiguation[col][0]
        return wd_uri

    if not isEnglishDbpediaUri(db_uri):
        db_uri = fromDbpediaToDbpediaUri(db_uri)
        if len(db_uri) == 0:
            return ''

        query = Q_DB_WD_SAMEAS.replace('STR_TO_SUB',db_uri)
        endpoint = detectEndpoint(db_uri)
        df_mapping_db_wd = getSPARQLResponse(query,endpoint)
        if len(df_mapping_db_wd) > 0:
            col = df_mapping_db_wd.columns[1]
            wd_uri = df_mapping_db_wd[col][0]
            return wd_uri

    return ''
    
def getDbpediaType(db_uri,q=Q_DB_TYPE):
    df = getSPARQLResponse(q.replace('STR_TO_SUB',db_uri),"http://dbpedia.org/sparql")
    if len(df)>0:
        col = df.columns[1]
        return list(df[col])
    else:
        return []
    
def fromWikidataToDbpediaUri(wd_uri,lang='en'):
    if lang == 'en':
        endpoint = "http://dbpedia.org/sparql"
        query = Q_WD_DB_SAMEAS.replace('STR_TO_SUB',wd_uri)
        df = getSPARQLResponse(query,endpoint)
        if len(df) > 0:
            col = df.columns[1]
            db_uri = df[col][0]
            return db_uri
        else:
            return ''
    else:
        endpoint = "http://"+lang+".dbpedia.org/sparql"
        query = Q_WD_DB_SAMEAS.replace('STR_TO_SUB',wd_uri)
        df = getSPARQLResponse(query,endpoint)
        if len(df) > 0:
            col = df.columns[1]
            db_uri = df[col][0]
            return db_uri
        endpoint = "http://dbpedia.org/sparql"
        query = Q_WD_DB_SAMEAS.replace('STR_TO_SUB',wd_uri)
        df = getSPARQLResponse(query,endpoint)
        if len(df) > 0:
            col = df.columns[1]
            db_uri = df[col][0]
        else:
            return ''
        return fromDbpediaToDbpediaUri(db_uri,lang=lang)
    return db_uri





def fromWikidataToWikipediaUri(wd_uri,lang='en'):
    wikidata_to_wikipedia = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=sitelinks&ids='
    wd_id = wd_uri.split('/')[-1]
    URL = wikidata_to_wikipedia + wd_id
    res = getRequestResult(URL)
    content = res.read()
    wiki_url = ''
    content = content.decode('utf8')
    try:
        obj = json.loads(content)
    except:
        raise Exception
        
    title = obj['entities'][wd_id]['sitelinks'][lang+"wiki"]['title']
    title = urllib.parse.quote(title)
    base = 'https://'+lang+'.wikipedia.org/wiki/'
    return base + title

def getWikiMissingInfo(wikipage):
    endpointURL='http://dbpedia.org/sparql'
    title = wikipage.split('/')[-1]
    wikistring = wikipage.replace("http:/", "https:/").replace(title, urllib.parse.quote(title))
    base_query = 'define sql:describe-mode "CBD"  DESCRIBE <STR_TO_SUB>'
    query = base_query.replace("STR_TO_SUB", wikistring)
    escapedQuery = urllib.parse.quote(query)
    requestURL = endpointURL + "?query=" + escapedQuery + "&output=text/csv"
    try:
        request = urllib.request.Request(requestURL)
        result = urllib.request.urlopen(request)
        df = pd.read_csv(result)
    except:
        return ''
    if len(df) > 0:
        df = df[df['predicate'] == 'http://schema.org/about'][['subject', 'object']]
        if len(df) > 0:
            return list(df['object'])[0]
    return ''

def fromWikipediaToWikidataUri(wiki_url):
    wikidata_base = 'http://www.wikidata.org/entity/'
    url_wikidpedia_to_wikidataid = "/w/api.php?action=query&prop=pageprops&format=json&titles=<TITLE>"
    base, title = wiki_url.split("/wiki/")
    URL = base + url_wikidpedia_to_wikidataid.replace('<TITLE>', urllib.parse.quote(title))
    res = getRequestResult(URL)
    wd_uri = ''
    content = res.read()
    if type(content) != str:
        content = content.decode('utf8')
    try:
        obj = json.loads(content)['query']['pages']
    except:
        print(content)
        raise Exception
    for k in obj:
        try:
            wd_uri = wikidata_base + obj[k]['pageprops']['wikibase_item']
            
        except:
            pass
    if wd_uri == '':
        return getWikiMissingInfo(wiki_url)
    return wd_uri



def getWikipediaPageLinks(wiki_url):
    wiki_url = wiki_url.replace('http:','https:')
    match = re.match("https://(.*)wikipedia",wiki_url)
    lang = match.group(1)[:-1]
    title = wiki_url.split('/')[-1]
    wiki_wiki = wikipediaapi.Wikipedia(lang)
    page_py = wiki_wiki.page(title)
    urls = list()
    for l in list(page_py.links.values()):
        try:
            urls.append(l.fullurl)
        except:
            pass
            
    return urls

def getWikipediaPageLangLinks(wiki_url,lang_):
    wiki_url = wiki_url.replace('http:','https:')
    match = re.match("https://(.*)wikipedia",wiki_url)
    lang = match.group(1)[:-1]
    title = wiki_url.split('/')[-1]
    wiki_wiki = wikipediaapi.Wikipedia(lang)
    page_py = wiki_wiki.page(title)
    links_dict = page_py.langlinks
    if lang in links_dict:
        page = links_dict[lang]
        try:
            return page.fullurl
        except:
            return None
    return None
