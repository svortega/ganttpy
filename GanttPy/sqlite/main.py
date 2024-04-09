# Copyright (c) 2022 steelpy
from __future__ import annotations
#
# Python stdlib imports
import os
import sqlite3 as sqlite3
from math import nan

#
# package imports


#
class DataBaseBasic:
    __slots__ = ['_conn', '_cursor', '_name']
    
    def __init__(self, db_file:None|str):
        """ """
        self._conn = None
        self._cursor = None
        if db_file:
            self.open(db_file)    
    
#
class SQLiteDB(DataBaseBasic):
    __slots__ = ['_conn', '_cursor', '_name']
    
    def __init__(self, db_file:None|str=None):
        """ """
        super().__init__(db_file=db_file)

    #
    def open(self, db_file:str):
        """ opens a new database connection"""
        try:
            self._conn = sqlite3.connect(db_file);
            self._cursor = self._conn.cursor()
        except sqlite3.Error as e:
            print("Error connecting to database!")
    #
    #
    def set_table(self, name:str, columns:dict) -> str:
        """Create new table"""
        newname = "tb_" + name
        table = f"CREATE TABLE IF NOT EXISTS {newname} ("
        table += ", ".join([f"{key} {item}" for key, item in columns.items()])
        table += ");"
        # push table
        try:
            self._conn.execute(table)
        except sqlite3.Error as e:
            raise RuntimeError(e)
        self._conn.commit()
    #
    def push_data(self, table_name:str, columns:list, data:list):
        """push data to table"""
        #
        newname = "tb_" + table_name
        table = f"INSERT INTO {newname} ("
        table += ", ".join([item for item in columns])
        table += ") VALUES( "
        table += ", ".join(["?" for item in columns])
        table += ")"
        #sql = 'INSERT INTO tb_Nodes(name, type,\
        #                            x, y, z, r, theta, phi)\
        #                            VALUES(?,?,?,?,?,?,?,?)'
        #cur = conn.cursor ()
        try:
            self._conn.executemany(table, data)
        except sqlite3.Error as e:
            raise RuntimeError(e)
        self._conn.commit()
    #
    def update_columns(self, table_name:dict, pivot:str,
                       columns:list, data:list):
        """ """
        newname = "tb_" + table_name
        #
        #table = f"UPDATE {newname} SET "
        #table += "=?, ".join([item for item in columns])
        for key, rows in pivot.items():
            table = f"UPDATE {newname} SET "
            table += "=?, ".join([item for item in columns])            
            #serie = ', '.join(f'{word}' for word in item)
            for idx, row in enumerate(rows):
                newtable = table + f"=? WHERE {key} = {row};"
                newdata = data[idx]
                try:
                    self._conn.execute(newtable, newdata)
                except sqlite3.Error as e:
                    raise RuntimeError(e)
        self._conn.commit()    
    #
    def close(self):
        """ close a database connection"""
        if self._conn:
            self._conn.commit()
            self._cursor.close()
            self._conn.close()
    #
    def __enter__(self):
        """ """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ """
        self.close()
    #
    def get(self, table:str, column:str,
            where:dict|None=None, limit:None|int=None):
        """ fetch/query data from a database  
        table: The name of the database's table to query from.
        columns: The string of columns, comma-separated, to fetch.
        limit: a limit of items to fetch (option).
        """
        if where:
            query = f"SELECT {column} from {table}"
            print('-->')
            for idx, (key, item) in enumerate(where.items()):
                try:
                    1/idx
                    query += f" AND {key} = '{item}'"
                except ZeroDivisionError:
                    query += f" WHERE {key} = '{item}'"
            query += ";"
        else:
            query = f"SELECT {column} from {table};"
        #
        self._cursor.execute(query)
        # fetch data
        rows = self._cursor.fetchall()
        rows = [find_replace(list(row), "NULL", nan) for row in rows]
        return rows[len(rows)-limit if limit else 0:]
    #
    def get_col_names(self, table:str):
        """ """
        columns = "*"
        query = f"SELECT {columns} from {table};"
        rows = self._cursor.execute(query)        
        return [x[0] for x in rows.description]
    #
    def get_last(self,table,columns):
        """ get the last row of data from a database"""
        return self.get(table, columns, limit=1)[0]
    #
    @staticmethod
    def to_csv(data,fname:str="output.csv"):
        """ converts a dataset into CSV format.  
        data : data, retrieved from the get() function.
        fname: file name to store the data in."""
        with open(fname, 'a') as file:
            file.write(",".join([str(j) for i in data for j in i]))
    #
    def write(self, table, columns, data):
        """ inserts new data into a table of the database.  
            table: The name of the database's table to write to.
            columns: The columns to insert into, as a comma-separated string.
            data : The new data to insert, as a comma-separated string.
            """
        query = f"INSERT INTO {table} ({columns}) VALUES ({data});"
        self._cursor.execute(query)
    #
    def query(self,sql):
        """ query any other SQL statement.  
        sql : A valid SQL statement in string format."""
        self._cursor.execute(sql)
    #
    @staticmethod
    def summary(rows):
        """ summarizes a dataset.  
        rows : The retrieved data.
        """
        # split the rows into columns
        cols = [ [r[c] for r in rows] for c in range(len(rows[0])) ]
        # the time in terms of fractions of hours of how long ago
        # the sample was assumes the sampling period is 10 minutes
        t = lambda col: "{:.1f}".format((len(rows) - col) / 6.0)
        # return a tuple, consisting of tuples of the maximum,
        # the minimum and the average for each column and their
        # respective time (how long ago, in fractions of hours)
        # average has no time, of course
        ret = []
        for c in cols:
            hi = max(c)
            hi_t = t(c.index(hi))
            #
            lo = min(c)
            lo_t = t(c.index(lo))
            #
            avg = sum(c)/len(rows)
            ret.append(((hi, hi_t), (lo, lo_t), avg))
        return ret    
#
#
def find_replace(arr,find,replace):
    """list find and replace"""
    try:
        while True:
            arr[arr.index(find)]=replace
    except ValueError:
        pass
    return arr
#
#
class SQLmodule:
    __slots__ = ['_db', '_cursor', '_name']
    
    def __init__(self, engine:str|None=None): # db_file=None|str, 
        """ """
        if not engine:
            self._db = SQLiteDB()
    #
    def read_db(self, db_name:str, table_name:str,
                column:str|None=None, where:dict|None=None):
        """
        db_name: database name
        table_name: table name
        column: colum name (default select all columns)
        where: select specific data from colum (default select all rows)
        """
        db_file = db_name + ".db"
        self._db.open(db_file=db_file)
        # get data
        table_name = "tb_" + table_name
        if column:
            data = self._db.get(table=table_name, column=column,
                                where=where)
            return data
        else:
            column = "*"
            data = self._db.get(table=table_name, column=column,
                                where=where)
            columns = self._db.get_col_names(table=table_name)
            return columns, data
    #
    #
    def edit_db(self, db_name:str, table_name:str,
                data, columns:dict, index:list|None=None):
        """ """
        db_file = db_name + ".db"
        self._db.open(db_file=db_file)
        self._db.set_table(name=table_name, columns=columns)
        #
        headers = list(columns.keys())
        if index:
            self._db.update_columns(table_name=table_name, 
                                    columns=headers, data=data, 
                                    pivot=index)
        else:
            self._db.push_data(table_name=table_name,
                               columns=headers, data=data)
        #
        self._db.close()
    #
    def update_cols(self, db_name:str, table_name:str, pivot:str,
                    columns:list, data:list):
        """ """
        db_file = db_name + "_f2u.db"
        self._db.open(db_file=db_file)
        #
        self._db.update_columns(table_name, pivot, columns, data)
        #
        self._db.close()
    #
    def clear_db(self, db_name):
        """delete existing db"""
        db_file = db_name + "_f2u.db"
        try:  # remove file if exist
            os.remove(db_file)
        except FileNotFoundError:
            pass
        
#
#
#
#