# Copyright (c) 2022 steelpy
from __future__ import annotations
#
# Python stdlib imports
#import os


#
# package imports
from GanttPy.spreadsheet.xl_main import Spreadsheet

#
class Reporting:
    __slots__ = ['_wb', '_ws_name', '_pm']
    
    def __init__(self, df):
        """ """
        self._pm = df
        self._wb = Spreadsheet()
        self._ws_name:str = "Progress_Report"
        #
        #wb_name = "excel_test"
        #wbout = self._reporting._wb.write_book()
        #ws = wbout.sheet_active(ws_name=ws_name)
        #ws["A1"] = "hello"
        #wbout.close(wb_name)        
    #
    def progress_out(self, group_report:dict,
                     columns:dict, wb_name:str,
                     select_items:dict|None=None):
        """ """
        new_df = self._pm.df.copy()
        if select_items:
            for name, drops in select_items.items():
                new_df = new_df.loc[new_df[name].isin(drops)]     
        #
        #
        ws_name = self._ws_name
        #
        for group, report in group_report.items():
            df = new_df.groupby(group)
            #
            col = 1
            row = 2          
            for i, key in enumerate(report):
                # set up excel
                wbout = self._wb.write_book()
                ws = wbout.sheet_active(ws_name=ws_name)
                ws["A1"] = list(columns.keys())
                #
                print(key)
                # get data frame group
                df2 = df.get_group(key)
                data = df2.groupby(['Asset', 'Project'])
                #
                for names, items in data:
                    print(names)
                    print(items)
                    nitem = items.Item.tolist()
                    newdata = items[list(columns.values())].astype('str')
                    newdata = newdata.values
                    newdata = newdata.tolist()
                    newdata = list(map(list, zip(*newdata)))
                    ws[col, row] = newdata
                    row += len(nitem) # + 1
                #    
                #          
                #
                new_name = f"{wb_name}_{group}_{key}"
                wbout.close(new_name)        
#
#
def get_progress_format(df):
    """ """
    by_provider = df.groupby("Contractor")
    providers = by_provider.groups.keys()
    providers = [key for key in providers]
    #providers
    wb = Workbook()
    wb.save("output.xlsx")
    #
    with pd.ExcelWriter("output.xlsx", mode="a") as writer:
        for provider in providers:
            df1 = by_provider.get_group(provider)
            df1.to_excel(writer, sheet_name=provider, startrow=3,
                         columns=["Project","CTR", "Scope", 
                                  "Start_Actual", "Duration_Actual", 
                                  "Finish_Actual", "Progress_Actual", 
                                  "Invoice_ToDate", "Forecast_Final"], 
                         header=["Project", "CTR", "Task", 
                                 "Start", "Duration", 
                                 "Planned Finish", "Progress", 
                                 "Invoice To Date", "Forecast To Final"],
                         index=True, index_label="ID")
    print('Finish')
#