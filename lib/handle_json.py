# Libraries
# library containign functions that map json data from cross ref

def jsonToPlainText(element):
    if isinstance(element, int) or \
       isinstance(element, float) or \
       isinstance(element, str):
        return element
    elif 'date-parts' in element:
        return element['date-parts'][0]
    elif 'issue' in element:
        return element['issue']
    elif isinstance(element, list) \
         and len(element) > 0 and 'URL' in element[0]:
        return element[0]['URL']

