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
        if None in value_list: value_list.remove(None)
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
    
    # get all values from the table using filter string
    def get_values(self, table, field, filter_str):
        str_query = "SELECT %s FROM %s WHERE %s" % (field, table, filter_str)
        value_list = self.connection.execute(str_query).fetchall( )
        return value_list


    # get row values from the table using filter string
    def get_row(self, table, id_val):
        str_query = "SELECT * FROM %s WHERE id = %s" % (table, id_val)
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
        #print (table, columns, values)
        str_query = "INSERT INTO %s %s VALUES %s " % (table, columns, values)
        # use cursor to get id of last inserted record
        a_cursor = self.connection.cursor()
        a_cursor.execute(str_query)
        ret_id = a_cursor.lastrowid
        self.connection.commit()
        return ret_id

    def set_value_table(self, table, field_id, column, value):
        str_query = "UPDATE %s SET %s = '%s' WHERE id = %s" % (table, column, value, field_id)
        if value == None or value == 'None':
            str_query = "UPDATE %s SET %s = NULL WHERE id = %s" % (table, column, field_id)
        self.connection.execute(str_query)
        self.connection.commit()
        return 0
    
    def add_column(self, table, column, db_type):
        str_query="ALTER TABLE %s ADD COLUMN %s %s;" %(table, column, db_type)
        #print(str_query)
        self.connection.execute(str_query)
        self.connection.commit()
        return 0
    
    def close(self):
        self.connection.close()
