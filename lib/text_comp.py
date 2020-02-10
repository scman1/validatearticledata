# Function to handle text matching and similarty

from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a,b).ratio()
