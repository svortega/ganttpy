# Copyright (c) 2022 ganttpy
from __future__ import annotations
#
# Python stdlib imports
import os
from datetime import datetime as dt, timedelta, date
from math import ceil
from random import choice
from typing import NamedTuple
#

#
# package imports
from GanttPy.pm.manager import ProjectManager
from GanttPy.pm.report import Reporting
from GanttPy.plots.ganttchart import GanttChart
from GanttPy.plots.budgetchart import BudgetDasboard
from GanttPy.sqlite.main import SQLmodule
from GanttPy.dataframe.dftime import get_week_year
from GanttPy.dataframe.dfseries import SeriesItem 
    

class ProGantt:
    __slots__ = ['_pm', '_sql'] # '_gantt', , '_reporting'
    
    def __init__(self):
        """
        """
        #
        self._sql = SQLmodule()
        #self._reporting = Reporting()
    #
    # ==========================================
    #
    def read_excel(self, wb_name:str, sheet_name:str|int,
                   skiprows:int=0, names:list|None=None):
        """ Read an Excel file into a DataFrame"""
        # get dataframe
        dataframe = self.xl2df(wb_name, sheet_name, 
                               skiprows, names=names)
        #
        # set PM
        self._pm = ProjectManager(dataframe)
    #
    #
    def xl2df(self, wb_name:str, sheet_name:str|int,
               skiprows:int|None=None, names:list|None=None):
        """ """
        try:
            import pandas as pd
            dataframe = pd.read_excel(wb_name, sheet_name=sheet_name, 
                                      names=names, skiprows=skiprows)
        except PermissionError:
            if not skiprows:
                skiprows = 1
            from GanttPy.spreadsheet.xl_main import Spreadsheet
            ss = Spreadsheet()
            wb = ss.read_book(wb_name)
            ws = wb.sheets[sheet_name]
            data = ws.get_data()
            data = data[skiprows-1:]
            try:
                idx = data[0].index(None)
            except ValueError:
                idx = -1                
            columns = data[0][:idx]
            data = [item[:idx] for item in data[1:]] 
            dataframe = self.to_df(data, columns=columns,
                                   db_name=sheet_name)
        except ModuleNotFoundError:
            if not skiprows:
                skiprows = 0          
            from GanttPy.spreadsheet.xl_main import Spreadsheet
            ss = Spreadsheet()
            wb = ss.read_book(wb_name)
            ws = wb.sheets[sheet_name]
            dataframe = ws.to_df(names=names, skiprows=skiprows,
                                 db_name=sheet_name)
        #print('--')
        return dataframe
    #
    def to_df(self,data: list|dict,
             columns: None|list = None,
             dtype:list|dict|None=None,
             parse_dates:list|None=None,
             db_name:str|None=None):
        """Covert data to df"""
        try:
            import pandas as pd
            dataframe = pd.DataFrame(data, columns=columns) #, dtype=dtype)
        except ModuleNotFoundError:
            from GanttPy.dataframe.dfsql import DataFrameSQL
            dataframe = DataFrameSQL(data, columns=columns, 
                                     db_name=db_name)
            #print('--')
        #
        #if parse_dates:
        #    for parse in parse_dates:
        #        dataframe[parse] = pd.to_datetime(dataframe[parse])
        #
        if dtype:
            dataframe = dataframe.astype(dtype=dtype)
        # set PM
        return dataframe
    #
    def setup_df(self, data: list|dict,
                 columns: None|list = None,
                 dtype:list|dict|None=None,
                 parse_dates:list|None=None):
        """ """
        #dtype = []
        #try:
        #    import pandas as pd
        #    dataframe = pd.DataFrame(data, columns=columns) #, dtype=dtype)
        #except ModuleNotFoundError:
        #    from GanttPy.dataframe.dfsql import DataFrameSQL
        #    dataframe = DataFrameSQL(data, columns=columns)
        #    print('--')
        #
        #if parse_dates:
        #    for parse in parse_dates:
        #        dataframe[parse] = pd.to_datetime(dataframe[parse])
        #
        #
        #if dtype:
        #    dataframe = dataframe.astype(dtype=dtype)
        dataframe = self.todf(data, columns,
                              dtype, parse_dates)
        # set PM
        self._pm = ProjectManager(dataframe)
    #
    # ==========================================
    #
    #
    @property
    def sql(self):
        """ """
        return self._sql
    #
    @property
    def pm(self):
        """ """
        return self._pm
    #    
    #@property
    #def df(self):
    #    """ """
    #    return self._pm._df
    #
    @pm.setter
    def pm(self, dataframe):
        """ """
        self._pm = ProjectManager(dataframe)    
    #
    @property
    def gantt(self):
        """ """
        return GanttChart(self._pm)
    #
    @property
    def report(self):
        """ """
        return Reporting(self._pm)
    #
    @property
    def dasboard(self):
        """ """
        return BudgetDasboard(self._pm)    
    #
    #
    # ==========================================
    # SQL project database
    #
    def delete_db(self, db_name):
        """ """
        self._sql.clear_db(db_name=db_name)
    #
    def new_project(self, db_name:str,
                    table_name:str, columns:dict,
                    df=None):
        #index: str | None = None,
        #year_list: list | None = None,
        #add_tables: list | None = None,
        """ """
        #
        if not df:
            df = self.pm.df
        # TODO: clear db?
        # self._sql.clear_db(db_name=db_name)
        # Main input data
        data = df.fillna("NULL")
        data = data.astype(str)
        data = data.values.tolist()
        self._sql.edit_db(db_name=db_name,
                          table_name=table_name,
                          data=data, columns=columns)
        #
    #
    def edit_project(self, db_name:str,
                    table_name:str, columns:dict,
                    index:list, df=None):
        #index: str | None = None,
        #year_list: list | None = None,
        #add_tables: list | None = None,
        """ """
        #
        #if not df:
        #    df = self.pm.df
        # TODO: clear db?
        # self._sql.clear_db(db_name=db_name)
        # Main input data
        data = df.fillna("NULL")
        data = data.astype(str)
        for key in index.keys():
            data = data.drop(key, axis=1)
            columns.pop(key, None)
        data = data.values.tolist()
        #
        #idx = {key:x for x, key in enumerate(columns.keys())}
        #
        self._sql.edit_db(db_name=db_name,
                          table_name=table_name,
                          data=data, 
                          columns=columns,
                          index=index)
        #
        #
        #if index:
        #    # set index 
        #    index_colum = {index:columns[index]}
        #    data_index = df[index].values.tolist()
        #    data_index = [(item,) for item in data_index]            
        #    #
        #    # -------------------------------------------------
        #    # Week year
        #    #
        #    if not year_list:
        #        currentYear = dt.now().year
        #        year_list = [currentYear]
        #    wnumber = get_week_year(year_list)
        #    add_colums = index_colum.copy()
        #    add_colums.update({item:"DECIMAL" for item in wnumber})
        #    #
        #    # -------------------------------------------------
        #    # set additioanal tables
        #    for table in add_tables:
        #        self._sql.new_db(project_name, 
        #                         table_name=table, 
        #                         columns=add_colums,
        #                         data=data_index,  index=[index])
        #
        print('---')
    #
    def to_sql(self, db_name:str="df_test"):
        """ """
        #
        db_file = db_name + "_f2u.db"
        try:  # remove file if exist
            os.remove(db_file)
        except FileNotFoundError:
            pass        
        #
        # -------------------------------------------------
        # sql section
        #table_name = "test_sql"
        #conn = sq.connect('{}.sqlite'.format(table_name)) # creates file
        #self._df.to_sql(table_name, conn, if_exists='replace', index=False) # writes to file
        #conn.close() # good practice: close connection
        #
        # reading
        #conn = sq.connect('{}.sqlite'.format(table_name))
        #df2 = pd.read_sql('select * from {}'.format(table_name), conn)
        #conn.close()
        #
        #
        #
        columns = {"Item":"INTEGER", "Asset":"TEXT", "Project":"TEXT", 
                   "Contractor":"TEXT", "PO":"TEXT", "CTR":"TEXT", "Scope":"TEXT", 
                   "Cost_Planned":"DECIMAL",
                   "Start_Planned":"TIMESTAMP", "Duration_Planned":"DECIMAL", 
                   "Start_Actual":"TIMESTAMP", "Duration_Actual":"DECIMAL", 
                   "Dependancy_Internal":"TEXT", "Dependancy_Interface":"TEXT",
                   "Department":"TEXT", "Project_Status":"TEXT", 
                   "Deadline_ID":"TEXT", "Deadline_Date":"TIMESTAMP"}
        #
        db = DataBaseSQL(db_file)
        table_name = "df"
        #
        df = self.df
        try:
            df["Duration_Planned"] = df["Duration_Planned"].dt.days
            df["Duration_Actual"] = df["Duration_Actual"].dt.days
        except AttributeError:
            pass
        #
        try:
            conn = db._conn
            table_name = "tb_" + table_name
            df.to_sql(table_name, conn, 
                      if_exists='replace', index=False)
            db.close()
        except:
            #
            db.set_table(name=table_name, columns=columns)
            #
            #col2 = {"Item":"INTEGER"}
            #col2.update(columns)
            #
            #headers = list(columns.keys())
            #
            #data = self._pm._df[headers].astype(str)
            #data = self._pm._df[headers].astype(str)
            data = df.fillna("NULL")
            data =  data.values.tolist()
            #columns = self._pm._df.columns.tolist()
            #
            #idx = [x for x, key in enumerate(col2.values())
            #       if key == "TIMESTAMP"]
            #
            #for row in data:
            #    for x in idx:
            #        date = row[x].strftime('%Y-%m-%d')
            #        date
            #
            db.push_data(data=data, table_name=table_name, header=columns)
        #
        print('---')
    #
    def read_project(self, db_name:str,
                     table_name:str, project_name:str,
                     parse_dates:dict|list|None=None,
                     columns:dict|list|None=None):
        """ """
        #
        #columns, data = self._sql.read_db(project_name, table_name=table_name)
        #newdata = list(map(list, zip(*data)))
        #
        #dtype = {'Start_Planned':'datetime64', 'Start_Actual':'datetime64', 'Deadline_Date':'datetime64'}
        #
        #self.setup_df(data=data, columns=columns, dtype=dtype)
        #
        where = {"Asset":project_name}
        columns, data = self._sql.read_db(db_name, table_name=table_name,
                                          column=columns, where=where)
        #
        #print('---')
        return self.to_df(data, columns, db_name=table_name)
    #
    def update_project(self, db_name:str,
                       table_name:str,
                       data:list|None = None,
                       columns:list|None=None, 
                       pivot:str|None=None):
        """ """
        if columns:
            self._sql.update_columns(db_name=db_name, table_name=table_name,
                                     pivot=pivot, columns=columns, data=data)
        else:
            1/0
    #
    def get_data(self, db_name:str, table_name:str, 
                 columns:list|None=None):
        """ """
        newdata = {}
        for column in columns:
            data = self._sql.read_db(db_name=db_name, 
                                     table_name=table_name,
                                     column=column)
            data = list(map(list, zip(*data)))
            newdata[column] = SeriesItem(data[0], name=column)
        return newdata
    #
    #
    def get_sql(self, db_name:str,
                table_name:str, 
                columns:dict|list|None=None):
        columns, data = self._sql.read_db(db_name, table_name=table_name,
                                          column=columns)
        #print('---')
        return self.to_df(data, columns, db_name=table_name)        
    #
    # ==========================================
    # reporting
    #
    #
    #
    # ==========================================
    #
    #
    #
    def progress_in(self, wb_name:str, sheet_name:str|int,
                   skiprows:int=0, names:list|None=None):
        """ """
        dataframe = self.xl2df(wb_name, sheet_name, 
                               skiprows, names=names)
        return dataframe
    #
    #
    #def update_
    #
    # ==========================================
    # tools
    #
#
#
