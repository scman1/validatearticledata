import requests
import urllib
import json
from bs4 import BeautifulSoup

def findFromURI(name, uri, referents):
    result = ""
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.get(uri, headers = req_head)
        soup = BeautifulSoup(response.text,'html.parser')
        paras = soup.find_all('span')
        heywords=referents
        best_match = likely = 0
        for para in paras:
            for keyword in heywords:
                if keyword in str(para).lower():
                    likely += 1
            if likely > 0:
                if result == "" or likely > best_match:
                    result = str(para)
                    best_match = likely
                    likely = 0
                elif likely == best_match:
                    result = result + "\n" + str(para)
                    best_match = likely
                    likely = 0
                else:
                    likely = 0
    except Exception as e:
        print(e)
    return result

def findURIFrag(uri, referents, contains):
    result = ""
    try:
        req = urllib.request.Request(uri)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        article_page = urllib.request.urlopen(req)
        page_text = article_page.read()
    except Exception as e:
        page_text=""
        print(e)
    for token in referents:
        start = str(page_text).lower().find(token.lower())
        if start > 0:
            end = start + 800
            result = str(page_text)[start:end]
            referred = result.lower().find(contains)
            if not referred > 0:
                result = "not found in ack"
            break
    return result

def findFromDOI(name, doi, referents):
    doi_url = 'https://dx.doi.org/'+ doi
    result = findFromURI(name, doi_url, referents)        
    return result

def getPageFromDOI (doi):
    doi_url = 'https://dx.doi.org/'+ doi
    page_text = ""
    try:
        req = urllib.request.Request(doi_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        article_page = urllib.request.urlopen(req)
        page_text = article_page.read()
    except Exception as e:
        print(e)
    return page_text

def getPageFromURL(url_text):
    page_text = ""
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.get(url_text, headers = req_head)
        page_text = response.text
    except Exception as e:
        print(e)
    return page_text

def getPageHeader(url_text):
    response = None
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        response = requests.head(url_text, headers = req_head)
    except Exception as e:
        print(e)
    return response

def getObject(url_text, store_at = "do_files/"):
    ret_object = {}
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        print('trying to recover object from', url_text)
        response = requests.get(url_text, headers = req_head)
        if response.status_code == 200:
            #print ('got something back')
            ret_object['resource_url'] = response.url
            #print ('resource url', ret_object['resource_url'])
            if 'content-type' in response.headers.keys():
                ret_object['type'] = response.headers['content-type']
            if 'content-length' in response.headers.keys():
                ret_object['size'] = response.headers['content-length']
            #name file using the url fragment after the last /
            fname = response.url.split("/")[-1:][0] 
            #print(fname)
            ret_object['file_name']  = store_at + fname
            with open(ret_object['file_name'], 'wb') as f:
                f.write(response.content)
    except Exception as e:
        print(e)
    finally:
        return ret_object

# try to get the object's metadata from DOIs
req_accepts = ['application/x-bibtex', 'application/x-research-info-systems', 'application/vnd.citationstyles.csl+json']
def getObjectMetadata(url_text, req_accept = 2):
    ret_object = {}
    try:
        req_head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
        req_head['Accept'] = req_accepts[req_accept]
        print('trying to recover object from', url_text)
        response = requests.get(url_text, headers = req_head)
        if response.status_code == 200:
            print ('got something back')
            ret_object['resource_url'] = response.url
            print ('resource url', ret_object['resource_url'])
            if 'content-type' in response.headers.keys():
                ret_object['type'] = response.headers['content-type']
            if 'content-length' in response.headers.keys():
                ret_object['size'] = response.headers['content-length']
            #name file using the url fragment after the last /
            if req_accept == 2:
                contents_json = json.loads(response.content.decode())
                ret_object['metadata'] = contents_json
            else:
               ret_object['metadata'] = contents.decode()
    except Exception as e:
        print(e)
    finally:
        return ret_object
