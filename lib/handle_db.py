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


    # get table structure
    def get_table_info(self, table):
        str_query = "PRAGMA table_info(%s) " % (table)
        values = self.connection.execute(str_query).fetchall( )
        return values 

    # get all table values
    def get_full_table(self, table):
        str_query = "SELECT * FROM %s " % (table)
        values  = self.connection.execute(str_query).fetchall( )
        return values 


    # get a value from the table using and id field
    def get_value(self, table, field, id_field, id_value):
        str_query = "SELECT %s FROM %s WHERE %s = '%s'" % (field, table, id_field, id_value)
        one_value = self.connection.execute(str_query).fetchone( )
        return one_value
    
    # get a values from the table using filter string
    def get_values(self, table, field, filer_str):
        str_query = "SELECT %s FROM %s WHERE %s" % (field, table, filer_str)
        value_list = self.connection.execute(str_query).fetchall( )
        return value_list


    def get_title(self, art_doi=""):
        title = self.connection.execute(
            "SELECT title FROM articles WHERE doi='%s'" % art_doi).fetchone( )
        return title

    def put_values_table(self, table, columns, values):
        columns = str(tuple(columns)).replace("'", "")
        values = str(tuple(values))
        if ' None, ' in values:
            values = values.replace(" None,", " NULL,").replace("(None,", "(NULL,").replace(", None)", ", NULL)")
        str_query = "INSERT INTO %s %s VALUES %s " % (table, columns, values)
        self.connection.execute(str_query)
        self.connection.commit()
        return 0
