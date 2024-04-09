# Copyright (c) 2022 ganttpy
#
# Python stdlib imports
from datetime import datetime as dt, date

#
# package imports
from GanttPy import ProGantt, Spreadsheet


def main(wb_name:str, sheet_name:str,
         group_list:list, skiprows:int=1,
         pivot_sheet="HandShake"):
    """ """
    #wb = xw.Book.caller()
    #wb_name = xw.books.active.name
    #
    #sheet = wb.sheets["Master"]
    #cells = sheet.range('A1').expand()
    #for x, row in enumerate(cells.rows):
    #    #PO = sheet.range(x+1, 1).value
    #    print(row[0].value)
    #
    if group_list:
        assets_list = group_list
    else:
        # FIXME
        assets_list = []
    #
    #db_name = wb_name
    #year_list = [2022]
    #add_tables = ["scope_progress", "invoice", "manhour_consumed"]    
    #
    # ------------------------------------------------------------
    #
    ss = Spreadsheet()
    wb = ss.read_book(wb_name)
    sheets = wb.sheet_names
    if sheet_name in sheets:
        ws = wb.sheets[sheet_name]
    else:
        raise IOError("Pivot sheet not found")
    #
    #col_test = ws.column["A"]
    #row_test = ws.row[1]
    #
    region = ws['B3']
    org = ws['B4']
    db_name = f"{region}_{org}"
    #
    #
    # ------------------------------------------------------------
    #
    project = ProGantt()
    #
    #
    table_name = sheet_name
    index = "Item"
    #
    #
    #
    # ------------------------------------------------------------
    # read existing project
    #project.read_project(project_name=project_name, 
    #                     table_name=table_name)
    #
    # ------------------------------------------------------------
    # fill missing df data
    #
    #ffill = ["Asset", "Project", "Vendor", "PO", "Project_Status"] # "Department",
    #fillna = None # {'Comments':'NTR'}
    #project.pm(ffill=ffill, fillna=fillna)
    #
    #
    # ------------------------------------------------------------
    # new/edit project
    #
    if table_name == "Project_BaseData":
        operation = ws['D2']
        #
        #
        if operation.lower() in ["new"]:
            #
            columns, ffill = read_sheet(project, wb_name, skiprows)
            #
            fillna = None # {'Comments':'NTR'}
            project.pm(ffill=ffill, fillna=fillna)            
            #
            project.new_project(db_name=db_name,
                                 table_name=table_name,
                                 columns=columns)         
            #
            #add_tables = ['start_actual', 'duration_actual', 'progress_actual', 'manhour_consumed',
            #              'invoice_todate', 'manhour_forecast', 'invoice_forecast',
            #              'comments']
            #
            #project.new_project(project_name=project_name,
            #                    table_name=table_name,
            #                    columns=columns, index=index)
            #                    #year_list=year_list,
            #                    #add_tables=add_tables)
        else:
            #
            project_name = ws['D3']
            #
            #upload_data(project, db_name,
            #            table_name, project_name,
            #            wb_name, ss, ws)
            #
            #
            # ------------------------------------------------------------
            # update existing project
            #
            df, columns = read_sheet(project, wb_name, skiprows)
            #
            #
            df.Item = df.Item .astype(dtype=int)
            index = {"Item": [str(int(item)) for item in df.Item.tolist()]}
            project.edit_project(df=df, 
                                 db_name=db_name,
                                 table_name=table_name,
                                 columns=columns,
                                 index=index)
    #
    else:
        # Input
        project_name = ws['D3']
        project_scope = ws['D4']
        vendor = ws['D5']
        project_status = ws['D6']
        PM = ws['D7']
        #
        groupby = ["Asset"]
        get_group = []
        if project_name:
            get_group.append(project_name)
        
        if project_scope:
            get_group.append(project_scope)
            groupby.append("Project")
        
        if PM:
            get_group.append(PM)
            groupby.append("PM_Email")
        
        if vendor:
            get_group.append(vendor)
            groupby.append("Vendor")
        
        if project_status:
            get_group.append(project_status)
            groupby.append("Project_Status")
        #
        # ------------------------------------------------------------
        # Upload data
        dbdata = project.get_sql(db_name=db_name,
                                 table_name="Project_BaseData")
        # Projects
        pj_group = dbdata.groupby(["Asset", "Project", "Project_Status",
                                   "Vendor", "Vendor_Email", "PM_Email"])
        pj_group = list(pj_group.groups.keys())
        #
        # ------------------------------------------------------------
        # write data to DB_Pivot sheet
        wspvt = wb.sheets["DB_Pivot"]
        wspvt["A2"] = pj_group
        #wb.save()
        #
        #
        #pm_group = dbdata.groupby(["PM_Email"])
        #pm_set = pm_group.get_group(PM)
        #
        #pj_group = pm_set.groupby("Asset")
        #pj_set = pj_group.get_group(project_name)
        #
        # ------------------------------------------------------------
        # Read sheet data
        #dataframe = project.xl2df(wb_name=wb_name,
        #                          sheet_name=sheet_name,
        #                          skiprows=skiprows)
        #
        1/0
        # ------------------------------------------------------------
        #currentYear = dt.now()
        #currentDate = dt(currentYear.year, currentYear.month, currentYear.day)
        #col_name = [f"W{currentDate.isocalendar()[1]}_{currentYear.year}"]
        ##
        #table_name = "progress_actual"
        #col_data = project.df["Progress_Actual"].tolist()
        #items = project.df[index].tolist()
        #col_data = [(col, items[x]) for x, col in enumerate(col_data)]
        ##
        #project.update_project(db_name=db_name,
        #                       table_name=table_name,
        #                       data=col_data, columns=col_name,
        #                       pivot=index)  
        #
        # ------------------------------------------------------------
        # get project progress
        #
        #progress = project.get_data(project_name=project_name,
        #                            table_name=table_name,
        #                            columns=col_name)
        #
        # ------------------------------------------------------------
        ## Print out reporting
        #week_name = date.today()
        #week_name = week_name.strftime('%U_%Y')
        #week_name = f"TEdB_Week_{week_name}"
        ##
        #group_report = {'Contractor':["NSG"]}
        #
        #columns =  {"Item": "Item", "Project":"Asset", "Name":"Project",
        #            "PO": "PO", "CTR":"CTR", "Task":"Scope",
        #            "Start":"Start_Actual", "Duration": "Duration_Actual",
        #            "Progress": "Progress_Actual"}
        #
        #select_items = {"Project_Status":["LIVE"]}
        #
        #project.report.progress_out(columns=columns,
        #                            group_report=group_report,
        #                            wb_name=week_name,
        #                            select_items=select_items)
        ##
        # ------------------------------------------------------------
        # Read progress report
        ##
        #weekly_report = "Week_30_2022_NSG.xlsx"
        #names = ["Item", "Asset","Project", "PO", "CTR", "Scope",
        #         "Start_Actual", "Duration_Actual", "Progress_Actual",
        #         "Invoice_ToDate", "Manhour_ToDate"]
        #reportdf = project.progress_in(wb_name=weekly_report,
        #                               sheet_name="Progress_Report",
        #                               skiprows=0, names=names)
        ##
        #new_data = reportdf[[index, "Progress_Actual"]].copy()
        ##
        #old_data = project.pm.df
        #old_data.set_index(index, inplace=True)
        #old_data.update(new_data.set_index(index))
        #old_data.reset_index(inplace=True)  # to recover the initial structure
        ##
        ##
        #col_data = old_data["Progress_Actual"].tolist()
        #items = old_data[index].tolist()
        #col_data = [(col,items[x]) for x, col in enumerate(col_data)]
        ##
        #project.update_project(project_name=project_name,
        #                       table_name=table_name,
        #                       data=col_data, columns=col_name,
        #                       pivot=index)
    ##
    # ------------------------------------------------------------
    # Plott gantt chart
    #
    #
    #project_group={"Asset":assets_list}
    #select_items = {"Project_Status":["LIVE", "PENDING", "DELIVERED", "HOLD"]}
    #project.gantt.plot(plot_name=project_name,
    #                   project_group=project_group,
    #                   select_items=select_items)
    #                   #project_progress=progress[col_name[0]])
    #
    #
    #
    # ------------------------------------------------------------
    # Budget Dasboard  
    #
    #report_list = ["Project"]
    #project.dasboard.plot(plot_name=project_name,
    #                      project_list=report_list)
    #
    print('--End')
#
#
def read_sheet(project, wb_name, skiprows):
    """ """
    # ------------------------------------------------------------
    # Handshake
    #
    handshake = project.xl2df(wb_name=wb_name,
                              sheet_name="HandShake")
    #
    # ------------------------------------------------------------
    # read excel data
    #project.read_excel(wb_name, sheet_name,
    #                   skiprows=skiprows,
    #                   names=list(columns.keys()))
    #
    dataframe = project.xl2df(wb_name=wb_name,
                              sheet_name=sheet_name,
                              skiprows=skiprows)
    #
    #
    # ------------------------------------------------------------
    # postprocessing
    #
    sheet_header = dataframe.columns.values.tolist()
    hshake_list = handshake["Sheet Header"].tolist()
    columns = {}
    for header in sheet_header:
        for idx, item in enumerate(hshake_list):
            if item == header:
                columns[handshake["SQL Header"].iloc[idx]] = handshake["Variable Type"].iloc[idx]
                break
    #
    by_group = handshake.groupby(["Missing Data"])
    by_ffill = by_group.get_group("forward fill")
    ffill = by_ffill["SQL Header"].tolist()
    #
    dataframe.columns = list(columns.keys())
    #
    dataframe = dataframe.dropna(subset=['Item'])
    #
    dataframe[ffill] = dataframe[ffill].fillna(method='ffill')
    #
    #
    return dataframe, columns
#
#
def upload_data(project, db_name, 
                table_name, project_name,
                wb_name, ss, ws):
    """ """
    # ------------------------------------------------------------
    # Handshake
    #
    handshake = project.xl2df(wb_name=wb_name,
                              sheet_name="HandShake")
    #
    # ------------------------------------------------------------
    #
    pdata = project.read_project(db_name=db_name,
                                 table_name=table_name,
                                 project_name=project_name)
    #
    sheet_header = pdata.columns.tolist()
    #
    # ------------------------------------------------------------
    # postprocessing
    #
    hshake_list = handshake["SQL Header"].tolist()
    columns = {}
    for header in sheet_header:
        for idx, item in enumerate(hshake_list):
            if item == header:
                columns[handshake["Sheet Header"].iloc[idx]] = handshake["Variable Type"].iloc[idx]
                break    
    #
    pdata.columns = list(columns.keys())
    #
    # ------------------------------------------------------------
    # postprocessing    
    #
    #xxx = ws.row[10]
    #xxx = ws.row["A10"]
    #ws.row[20] = headers
    #ws.row["A20"] = headers
    #
    #yyy = ws.column["A2"]
    #yyy = ws.column[1]
    #ws.column["A20"] = pdata.Item.tolist()
    #
    #wsout = ss.write_book()
    #ws2 = wsout[sheet_name]
    #row = 11
    #
    #
    wsdf = ws.df_tools(header=True)
    wsdf["A10"] = pdata
    #
    #col = "A11" 
    #col = ss.cell_tools.get_col_number(col)
    #for idx, column in enumerate(headers):
    #    index = ss.cell_tools.cell_name(column=col[0]+idx, row=col[1])
    #    ws.column[index] = pdata[column].tolist()
    #
    print('-- Data Reloaded')
#
#
def reload_progress(dbdata, groupby):
    """ """
    # ------------------------------------------------------------
    # reload sheet
    #
    if get_group:
        pj_group = dbdata.groupby(groupby)
        get_group = [tuple(get_group)]
    else:
        pj_group = dbdata.groupby(["Asset", "Project"])
        get_group = list(pj_group.groups.keys())
    #
    wsdf = ws.df_tool(header=False)
    row = 20
    for item in get_group:
        col=1
        pjdf = pj_group.get_group(item)
        rowno = len(pjdf["Task"])
        #
        ws.column[col,row] = pjdf.Item.tolist()
        col += 1
        ws[col,row] = item[0]
        col += 1
        ws[col,row] = item[1]
        col += 1            
        #
        wsdf[col,row] = pjdf[["Task", "PM_Email", 
                              "Vendor", "Project_Status"]]
        row += rowno
    #    
#
#
if __name__ == "__main__":
    
    # Create groups
    # TEdB
    #workbook = "Progress_TEdB.xlsm"
    #assets_list = ["P65", "P08", "PCE-1", "PPM-1"]
    # TEGI
    #workbook = "Projects_TEGI.xlsm"
    #assets_list = ["FOXTROT", "ECHO", "CPF", "CEIBA"]
    #
    #sheet_name = "Master"
    #
    # New Project
    workbook = "Projects_Gantt.xlsm"
    assets_list = None
    sheet_name = "Project_BaseData"
    #sheet_name = "Project_Progress"
    #
    #xw.Book("projectplan_TEdB.xlsm").set_mock_caller()
    #xw.Book("projectplan_TEGI.xlsm").set_mock_caller()
    main(workbook, sheet_name, group_list=assets_list,
         skiprows=9)
