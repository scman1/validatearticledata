# libraries

from sqlite3 import dbapi2 as sqlite
from pathlib import Path

class DataBaseAdapter:
    
    #connection = None         # class variable shared by all instances

    def __init__(self, dbname):
        self.dbname = dbname    # instance variable unique to each instance
        self.connection = sqlite.connect(dbname)
        
    def get_value_list(self, table, field):
        results = self.connection.execute("SELECT %s FROM %s GROUP BY %s" % (field, table, field) ).fetchall( )
        value_list = []
        for result in results:
            for item in result:
                value_list.append(item)
        if '' in value_list: value_list.remove('')
        return value_list

    # get a value from the table using and id field
    def get_value(self, table, field, id_field, id_value):
        str_query = "SELECT %s FROM %s WHERE %s = '%s'" % (field, table, id_field, id_value)
        one_value = self.connection.execute(str_query).fetchone( )
        return one_value


    def get_title(self, art_doi=""):
        title = self.connection.execute(
            "SELECT title FROM articles WHERE doi='%s'" % art_doi).fetchone( )
        return title

