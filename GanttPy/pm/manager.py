# Copyright (c) 2022 steelpy
from __future__ import annotations
#
# Python stdlib imports
from collections import defaultdict
import datetime
from typing import NamedTuple
#import sqlite3 as sq


#
# package imports
from GanttPy.dataframe.dftime import today_floor, get_next_monday, get_past_monday
from GanttPy.dataframe.dfseries import to_timedelta


class ProjectDuration(NamedTuple):
    start_planned:list
    start_actual:list
    start_forecast:list

#
#
class ProjectManager:
    __slots__ = ['_df']
    
    def __init__(self, dataframe):
        """
        """
        # ======================================================================
        self._df = dataframe
        #self.__call__()
    #
    @property
    def df(self):
        """return dataframe"""
        return self._df
    #
    #@df.setter
    #def df(self, dataframe):
    #    """return dataframe"""
    #    self._df = dataframe
    #
    # ----------------------------------------------------------
    #
    # END FIXME
    # ---------------------------------------------------------
    #
    #
    def __call__(self, drop_items:dict|None=None,
                 ffill:list|None=None,
                 fillna:dict|None=None):
        """ """
        #
        #new_df = new_df.loc[self._df['Project_Status'] != "CANCEL"]
        #
        #
        # ======================================================================
        # forward filling
        if ffill:
            self._df[ffill] = self._df[ffill].fillna(method='ffill')
        #
        # ======================================================================
        # replace empty values
        if fillna:
            for key, value in fillna.items():
                self._df[key] = self._df[key].fillna(value) 
        #
        #
        # ======================================================================
        # Remove cancelled items
        #
        #print(self._df)
        #self._df = self._df.loc[self._df['Project_Status'] != "CANCEL"]
        #
        # ======================================================================
        #
        #print('---')
        #
        #print(self._df)
        # 
        #
        #return self._df
        #
        #
        #
        
    #
    #
    def dependencies(self, new_df, cutoff_date):
        """ """
        # ======================================================================
        # Calculations
        # ======================================================================
        #
        # Actual Porgress
        task = new_df.Item.astype(str)
        task = task.tolist()
        start = new_df.Start_Actual.copy()
        finish = new_df.Finish_Actual.copy()
        progress = new_df.Progress_Actual.fillna(0)
        #
        # Interfaces
        new_df.Dependancy_Interface = new_df.Dependancy_Interface.fillna(0)
        #print(new_df.Dependancy_Interface)
        start, finish = dependency_mod(task, start, finish, cutoff_date,
                                       new_df.Dependancy_Interface, progress)
        #
        # Internal
        new_df.Dependancy_Internal = new_df.Dependancy_Internal.fillna(0)
        #new_df["Start_Forecast"], new_df["Finish_Forecast"] = dependency_mod(task, start, finish, 
        #                                                                     new_df.Dependancy_Internal)
        #
        return dependency_mod(task, start, finish, cutoff_date,
                              new_df.Dependancy_Internal, progress)
    #
    def date_process(self, new_df):
        """ """
        # ======================================================================
        # set planned dates
        new_df.Duration_Planned = to_timedelta(new_df.Duration_Planned, unit="W")
        #print(new_df.Duration_Planned)
        #xyx = new_df.Start_Planned + new_df.Duration_Planned
        new_df["Finish_Planned"] = new_df.Start_Planned + new_df.Duration_Planned
        #print(new_df["Finish_Planned"])
        #
        # set finish actual stage 1
        today = datetime.date.today()
        next_monday = get_next_monday(today.year, today.month, today.day)
        start_actual = new_df.Start_Planned.apply(lambda x: next_monday if x < next_monday else x)
        new_df.Start_Actual = new_df.Start_Actual.fillna(start_actual)
        #
        # finish actual
        new_df.Duration_Actual = to_timedelta(new_df.Duration_Actual, unit="W")
        #duration_actual = new_df.Duration_Actual.apply(lambda x: next_monday if x < next_monday else x)
        new_df.Duration_Actual = new_df.Duration_Actual.fillna(new_df.Duration_Planned)
        new_df["Finish_Actual"] = new_df.Start_Actual + new_df.Duration_Actual
        #        
        # ======================================================================
        #
        #new_df["week_start_planned"] = new_df.Start_Planned.dt.to_period('W').dt.start_time
        #
        past_monday = get_past_monday(today.year, today.month, today.day)
        new_df["Start_Forecast"], new_df["Finish_Forecast"] = self.dependencies(new_df, past_monday)
        #
        return new_df
    #
    #
    def gantt_process(self, current_progress,
                      select_items:dict|None):
        """ """
        # ======================================================================
        #
        new_df = self._df.copy()
        #
        # ======================================================================
        # update actual data
        if current_progress:
            new_df["Progress_Actual"] = current_progress       
        #
        # ======================================================================
        #
        if select_items:
            for name, drops in select_items.items():
                new_df = new_df.loc[new_df[name].isin(drops)]       
        #
        # ======================================================================
        ## set planned dates
        #
        new_df = self.date_process(new_df)
        #
        #
        # ======================================================================
        # Calculations
        # ======================================================================
        #
        # Actual Porgress
        task = new_df.Item.astype(str)
        task = task.tolist()
        #
        # Forecast progress
        new_df["Finish_Risk"], new_df["Progress_Forecast"], deficit = get_risk_progress(new_df,
                                                                                        new_df.Start_Planned, 
                                                                                        new_df.Start_Forecast, 
                                                                                        new_df.Finish_Forecast)    
        #
        # Reset risk to forecast if task is on hold
        new_df["Finish_Risk"] = [new_df.Finish_Forecast.iloc[idx] if new_df.Project_Status.iloc[idx] == "HOLD" else item
                                 for idx, item in enumerate(new_df.Finish_Risk)]
        #
        new_df["Progress_Forecast"] = [new_df.Progress_Actual.iloc[idx] if new_df.Project_Status.iloc[idx] == "HOLD" else item
                                       for idx, item in enumerate(new_df.Progress_Forecast)]    
        # Internal dependency
        depen_rem = get_predecessors(task, new_df.Project_Status,
                                     new_df.Start_Forecast, new_df.Finish_Forecast,
                                     new_df.Dependancy_Internal, deficit)
        # Interface dependency
        depen_rem = get_predecessors(task, new_df.Project_Status, 
                                     new_df.Start_Forecast, new_df.Finish_Forecast,
                                     new_df.Dependancy_Interface, deficit, depen_rem)
        #
        indextd = list(depen_rem.keys())
        fdtd = [max(depen_rem[idx]) if idx in indextd else 0
                for idx,_ in enumerate(task)]
        #
        new_df["delta_days"] = [to_timedelta(days, unit="D") for days in fdtd]
        new_df["Finish_Risk"] = new_df["Finish_Risk"] + new_df["delta_days"] 
        #
        #for idx, item in depen_rem.items():
        #    days = max(item)
        #    new_df["Finish_Risk"].iloc[idx] +=  to_timedelta(days, unit="D")   
        #
        # ======================================================================
        #
        new_df["proj_start"] = new_df.Start_Forecast.min()
        new_df["risk_end_num"] = (new_df.Finish_Risk - new_df.proj_start).dt.days         
        #
        # convert to number
        new_df["start_num"] = (new_df.Start_Forecast - new_df.proj_start).dt.days
        new_df["end_num"] = (new_df.Finish_Forecast - new_df.proj_start).dt.days
        #
        return new_df
    #
    def cost_process(self):
        """ """
        new_df = self._df.copy()
        #
        #costs = new_df.Cost_Planned
        #task = new_df.Item
        #
        # ======================================================================
        # set planned dates
        new_df = self.date_process(new_df)
        #
        # ======================================================================        
        #print('---')
        return new_df
    #
#
#
#
#
#
#
def dependency_mod(indices, start, finish, today, dependancy, progress):
    """ """
    #1/0
    new_start = start.copy()
    new_finish = finish.copy()
    #task = tasks.tolist()
    steps = len(indices)
    for idx in range(steps):
        row = dependancy.iloc[idx]
        try:
            items = [int(row)]
        except ValueError:
            items = row.strip()
            items = items.split(',')
            items = [item for item in items]
        if items[0]:
            start_item = new_start.iloc[idx]
            #day_start = start_item.day_name()
            #if day_start == 'Monday':
            #    pass
            #
            for item in items:
                sinx = indices.index(str(item))
                end_item = new_finish.iloc[sinx]
                if start_item < end_item:
                    # check begining of the week Monday
                    try:
                        day = end_item.day_name()
                    except AttributeError:
                        day = end_item.strftime("%A")
                    if day != 'Monday':
                        monday_start = get_next_monday(end_item.year, 
                                                       end_item.month, 
                                                       end_item.day)
                        shift = monday_start - start_item
                    else:
                        shift = end_item - start_item
                    #
                    new_start.iloc[idx] = start.iloc[idx] + shift
                    new_finish.iloc[idx] = finish.iloc[idx] + shift
                    start_item = end_item
        #
        if new_finish.iloc[idx] < today:
            if progress.iloc[idx] < 100:
                #print("--->")
                new_finish.iloc[idx] = today
    #
    return new_start, new_finish
#
#
def get_risk_progress(df, week_start, start, finish):
    """ """
    #
    Finish_Forecast = finish.copy()
    today_num = (today_floor() - week_start.min()).days
    start_num, end_num, days_start_to_end = get_start_end(week_start, start, finish)
    start_from_today = today_num - start_num
    #
    rem_progress = []
    deficit = []
    #
    for x, progress in enumerate(df.Progress_Actual):
        if progress >= 100:
        #if end > 0:
            rem_progress.append(100)
            deficit.append(0)
        else:
            begining = start_from_today.iloc[x]
            if begining > 0:
                days_duration = days_start_to_end.iloc[x]
                progress_forecast = abs(begining/days_duration)
                rem_progress.append(round(progress_forecast*100))
                progress_nett = progress - rem_progress[x]
                if progress_nett < 0:
                    deficit.append(round(abs(progress_nett/100) * days_duration))
                    Finish_Forecast.iloc[x] =  finish.iloc[x] + to_timedelta(deficit[-1], unit="D")
                else:
                    deficit.append(0)
            else:
                rem_progress.append(0)
                deficit.append(0)
    #
    #print('---')
    return Finish_Forecast, rem_progress, deficit
#
#
def get_start_end(week_start, start, finish):
    """Get start and end of bar data"""
    # TODO: why this?
    #proj_end = finish.dt.normalize().map(MonthEnd(normalize=True).rollback)
    proj_end = finish
    #
    #week_start = start.dt.to_period('W').dt.start_time
    #print(week_start)
    proj_start = week_start.min()
    # number of days from project start to task start
    start_num = (start - proj_start).dt.days
    # number of days from project start to end of tasks
    end_num = (proj_end - proj_start).dt.days
    # days between start and end of each task
    days_start_to_end = end_num - start_num
    #
    return start_num, end_num, days_start_to_end
#
#
#class Dependency(NamedTuple):
#    """ """
#    successor:int|str
#    predecessors:list
#    #end_risks:list
#
def get_predecessors(Indices, status, 
                     Start_Forecast, Finish_Forecast,
                     dependancy, deficit, 
                     rem_dependency:dict|None=None):
    """ """
    #1/0
    if not rem_dependency:
        rem_dependency = defaultdict(list)
    #   
    for index in Indices:
        idx = Indices.index(index)
        row = dependancy.iloc[idx]
        #risk_succ = risk_end.iloc[idx]
        try:
            items = [int(row)]
        except ValueError:
            items = row.strip()
            items = items.split(',')
            items = [int(item) for item in items]        
        #
        if items[0]:
            for item in items:
                pre_index = Indices.index(str(item))
                #risk_pred = risk_end.iloc[pre_index]
                if status.iloc[pre_index] == "HOLD":
                    #print(f'--> {index} : {item}')
                    continue
                #
                if deficit[pre_index]:
                    # get dependency start
                    dstart = Start_Forecast.iloc[idx]
                    # get predecesor end
                    pend = Finish_Forecast.iloc[pre_index]
                    # filter task with predecesors end > dependency start
                    if pend >= dstart:
                        rem_dependency[idx].append(deficit[pre_index])
                    #print('--')
    #
    #
    return rem_dependency
#
#