# Copyright (c) 2022 steelpy
from __future__ import annotations
#
# Python stdlib imports
from collections import defaultdict
#from math import isnan
#import datetime
#from typing import NamedTuple
from itertools import accumulate, cycle
from datetime import datetime as dt, date

#
# package imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.dates import date2num
#
from GanttPy.dataframe.dfseries import time_delta, to_timedelta
from GanttPy.dataframe.dftime import (first_dow, monday_of_calenderweek,
                                      date_range, date_offset, today_floor)
#
#
class BudgetDasboard:
    __slots__ = ['_bar_colors', '_project_list', 'pm', 'by_asset']
    
    def __init__(self, pm):
        """
        """
        self.pm = pm
    #
    def __call__(self, project_list:list):
        """ """
        #
        mdf = self.pm.cost_process()
        #
        total_budget = mdf.Project_Budget.sum()
        #        
        # ======================================================================
        #  Start iteration
        # ======================================================================
        #        
        #
        #week_start_planned = mdf.week_start_planned
        #
        start_date = mdf.Start_Forecast.min() - date_offset(months=1)
        end_date = mdf.Finish_Forecast.max() + date_offset(months=2)
        #months = end_date.to_period("M") - start_date.to_period("M")
        months = date_range(start_date, end_date, freq="MS")
        monthslen = len(months)
        #
        #mdf["time_period"] = start_date.floor("M")
        #
        # ======================================================================
        #
        #currentYear = dt.now()
        #currentDate = dt(currentYear.year, currentYear.month, currentYear.day)
        #first_year_monday = first_dow(year=currentYear.year, month=1)
        #first_monday = monday_of_calenderweek(year=currentYear.year, week=1)
        #
        #
        # ======================================================================
        #
        by_group = mdf.groupby(project_list)
        key_groups = by_group.groups.keys()
        #
        #
        #
        #
        # ======================================================================
        #
        new_group = {}
        progress_montly = {}
        invoices = {}
        montly_cash = [0 for item in range(monthslen)]
        #
        for i, key in enumerate(key_groups):
            # get data frame group
            df2 = by_group.get_group(key)
            invoices[key] = 0
            progress_montly[key] = 0
            new_group[key] = df2.Cost_Planned.sum()
            for idx in range(monthslen-1):
                start_month = months[idx]
                end_month = months[idx+1]
                gap = df2[df2.Finish_Planned.between(start_month, end_month)]
                if gap.Item.empty:
                    continue
                else:
                    #print(f'---{key} {start_month} {end_month}')
                    #print(gap.Cost_Planned)
                    montly_cash[idx+1] += gap.Cost_Planned.sum()
        #
        cumulative_cash = list(accumulate(montly_cash))
        #
        # ======================================================================
        #
        fig, ax = plt.subplots(2,1, figsize=(16,10))
        #fig, ax = plt.subplots()
        #
        # ======================================================================
        # Plot summary
        #
        bottom = list(new_group.values())
        bottom.insert(0, 0)
        bottom = list(accumulate(bottom))
        bottom[-1] = 0
        new_group.update({"Total":total_budget})
        progress_montly.update({"Total":0})
        invoices.update({"Total":0})
        plot_summary(ax[0], new_group, bottom, progress_montly, invoices)
        #
        # ======================================================================
        # plot comulative cash flow
        #
        plot_cash_flow(ax[1], months, montly_cash, cumulative_cash)
        #
        # ======================================================================
        #
        fig.tight_layout()
        #
        #plt.grid(True, 'major', 'both', ls='--', lw=.5, c='k', alpha=.3)
        #plt.ylim(0, max(cumulative_cash)*1.1)
        # 
        #plt.show()        
        #
    def plot(self, plot_name:str, project_list:list):
        """ """
        #
        self.__call__(project_list)
        #
        week = date.today()
        week = week.strftime('%U-%Y')
        fgname = f"cost_{plot_name}_Week_{week}.png"
        plt.savefig(fgname)
        #
        print('here')
#
#
def plot_summary(ax, new_group, bottom, progress_montly, invoices_todate):
    """ """
    # Plotting
    length = len(new_group)
    dem = 1000 # factor cash unit
    data = [item/dem for item in new_group.values()]
    bottom = [item/dem for item in bottom]
    #
    #
    week = date.today()
    week = week.strftime('%U_%y')
    #week = Timestamp.today()
    #week = week.strftime('%U') # -%Y
    #
    # ======================================================================
    # 
    # Set plot parameters
    width = 0.2 # width of bar
    x = [i-width*0.50 for i in range(length)]
    #
    # budget
    ax.bar(x, data, width, bottom=bottom,
           color="green", alpha=0.4,
           label='Budget', align="center", 
           edgecolor='green', linewidth=1.5)
    #
    # "orangered"
    # Invoices
    width2 = 0.10
    #
    invoices = [item for item in invoices_todate.values()] 
    xshift = [item for item in x]
    ax.bar(xshift , invoices, width2, bottom=bottom,
           color="green", alpha=1.0, 
           label='Invoices')
    #
    # Progress Planned
    xshift = [item + width for item in x]
    ax.bar(xshift , data, width, bottom=bottom,
           color='darkorchid', alpha=0.4, 
           label='Progress', align="center", 
           edgecolor='darkorchid', linewidth=1.5)
    #
    # Progress actual
    progress =  [item for item in progress_montly.values()]
    xshift = [item + width for item in x]
    ax.bar(xshift , progress, width2, bottom=bottom,
           color='darkorchid', alpha=1.0, 
           label='Progress', align="center", 
           edgecolor='darkorchid', linewidth=1.5)         
    #
    #x-axis format
    #
    # ======================================================================
    #ax.axis('off')
    #
    x_labels = list(new_group.keys())
    x_dim = [item + width*0.50 for item in x]
    ax.set_xticks(x_dim)
    ax.set_xticklabels(x_labels)
    #ax.set_xlabel(f'{project_list[0]}')
    #
    #
    # 
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
        label.set_fontname('Consolas')
        label.set_fontsize(8)
    #
    # ======================================================================
    # y-axis format
    #
    #ax.set(yticklabels=[])
    #
    fmt = '{x:,.0f}K'
    tick = mtick.StrMethodFormatter(fmt)
    ax.yaxis.set_major_formatter(tick)
    #
    # Project Budget
    height = [item + bottom[x] for x, item in enumerate(data)]
    xshift = [item - width for item in x]
    for i in range(length):
        ax.text(xshift[i], height[i], 
                '${:,.0f}K'.format(data[i]), 
                rotation=90, fontsize=8, fontfamily='Consolas')
    #
    # Invoiced
    #
    #xshift = [item for item in x]
    for i in range(length):
        ax.text(x[i], height[i], 
                '  ${:,.0f}K Week_{:}'.format(invoices[i], week), 
                rotation=90, fontsize=8, fontfamily='Consolas',
                horizontalalignment='center')
    #
    # Progress
    #
    xshift = [item + width for item in x]
    for i in range(length):
        ax.text(xshift[i], height[i], 
                '  {:.0f}% Week_{:}'.format(progress[i], week), 
                rotation=90, fontsize=8, fontfamily='Consolas',
                horizontalalignment='center')        
    #
    ax.set_ylim(0, max(height)*1.1)
    ax.grid(True, 'major', 'both', ls='--', lw=.5, c='k', alpha=.3)
    #
    #
    title = "Invoice Vs Progress"
    ax.set_title(title, loc='center',
                 fontfamily="Consolas", fontweight="bold",
                 color="black", fontsize=12)
    #
    #
    # Title --> to be moved
    #
    title = "Okume Ceiba Subsea TieBack"
    ax.set_title(title, loc='left',
                 fontfamily="Calibri", fontweight="bold",
                 color="forestgreen", fontsize=16)  #  y=0.85, x=0.02, # midnightblue
    #
    #
#
#
def plot_cash_flow(ax, months, montly_cash, cumulative_cash):
    """ """
    #
    monthslen = len(months)
    width = 0.4 # width of bar
    dem = 1000 # factor cash unit
    #
    #ax = plt.subplot(111)
    x = list(range(monthslen))
    #x = [item for item in range(monthslen)]
    #x = date2num(months)
    montly_cash = [item/dem for item in montly_cash]
    #
    #
    #data = {item: [montly_cash[i], montly_cash[i]] 
    #        for i, item in enumerate(months)}
    #bar_plot(ax, data, legend=False)
    #
    # Planned
    xshift = [item-width*0.5 for item in x]
    ax.bar(xshift, montly_cash, width=width,
           color="green", alpha=0.80, #align="center", 
           edgecolor='green', linewidth=1.5)
    #
    # Actual/Forecast
    xshift = [item+width*0.5 for item in x]
    ax.bar(xshift, montly_cash, width=width,
           color="orangered", alpha=0.80, #align="center", 
           edgecolor='orangered', linewidth=1.5)
    #
    #
    # Comulative curve
    # getting data of the histogram
    #count, bins_count = np.histogram(cumulative_cash, bins=len(cumulative_cash)-1)    
    # finding the PDF of the histogram using count values
    #pdf = count / sum(count)
    # using numpy np.cumsum to calculate the CDF
    # We can also find using the PDF values by looping and adding
    #cdf = np.cumsum(pdf)
    #cumulative_cash = [cdf[i]*item/dem for i, item in enumerate(cumulative_cash)]
    #cumulative_cash = bins_count / dem
    cumulative_cash = [item/dem for  item in cumulative_cash]
    #
    #Plan
    ax.plot(x, cumulative_cash, linestyle='-', 
            color="green", linewidth=4, label='Planned')
    #
    # Forecast/Actual
    ax.plot(x, cumulative_cash, linestyle='-', 
            color="orangered", linewidth=2, label='Forecast')    
    #
    #ax.set_xlim(xmin=1)
    #ax.xaxis_date()
    #
    x_labels = [item.strftime("%d/%m/%y") for item in months]
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
        label.set_fontname('Consolas')
        label.set_fontsize(8)        
    #
    fmt = '{x:,.0f}K'
    tick = mtick.StrMethodFormatter(fmt)
    ax.yaxis.set_major_formatter(tick)        
    #
    ax.set_ylim(0, max(cumulative_cash)*1.1)
    ax.grid(True, 'major', 'both', ls='--', lw=.5, c='k', alpha=.3)
    #
    #ax.set_xlim(xmin=1)
    title = "Montly Cost Forecast"
    ax.set_title(title, loc='center',
                 fontfamily="Consolas", fontweight="bold",
                 color="black", fontsize=12)
    #
    ax.legend(loc="upper left")
    #print('---')
#
#
def bar_plot(ax, data, group_stretch=0.8, bar_stretch=0.95,
             legend=True, x_labels=True, label_fontsize=8,
             colors=None, barlabel_offset=1,
             bar_labeler=lambda k, i, s: str(round(s, 3))):
    """
    Draws a bar plot with multiple bars per data point.
    :param dict data: The data we want to plot, wher keys are the names of each
      bar group, and items is a list of bar values for the corresponding group.
    :param float group_stretch: 1 means groups occupy the most (largest groups
      touch side to side if they have equal number of bars).
    :param float bar_stretch: If 1, bars within a group will touch side to side.
    :param bool x_labels: If true, x-axis will contain labels with the group
      names given at data, centered at the bar group.
    :param int label_fontsize: Font size for the label on top of each bar.
    :param float barlabel_offset: Distance, in y-values, between the top of the
      bar and its label.
    :param function bar_labeler: If not None, must be a functor with signature
      ``f(group_name, i, scalar)->str``, where each scalar is the entry found at
      data[group_name][i]. When given, returns a label to put on the top of each
      bar. Otherwise no labels on top of bars.
    """
    sorted_data = list(sorted(data.items(), key=lambda elt: elt[0]))
    sorted_k, sorted_v  = zip(*sorted_data)
    max_n_bars = max(len(v) for v in data.values())
    group_centers = np.cumsum([max_n_bars
                               for _ in sorted_data]) - (max_n_bars / 2)
    bar_offset = (1 - bar_stretch) / 2
    bars = defaultdict(list)
    #
    if colors is None:
        colors = {g_name: [f"C{i}" for _ in values]
                  for i, (g_name, values) in enumerate(data.items())}
    #
    for g_i, ((g_name, vals), g_center) in enumerate(zip(sorted_data,
                                                         group_centers)):
        n_bars = len(vals)
        group_beg = g_center - (n_bars / 2) + (bar_stretch / 2)
        for val_i, val in enumerate(vals):
            bar = ax.bar(group_beg + val_i + bar_offset,
                         height=val, width=bar_stretch,
                         color=colors[g_name][val_i])[0]
            bars[g_name].append(bar)
            if  bar_labeler is not None:
                x_pos = bar.get_x() + (bar.get_width() / 2.0)
                y_pos = val + barlabel_offset
                barlbl = bar_labeler(g_name, val_i, val)
                ax.text(x_pos, y_pos, barlbl, ha="center", va="bottom",
                        fontsize=label_fontsize)
    if legend:
        ax.legend([bars[k][0] for k in sorted_k], sorted_k)
    #
    ax.set_xticks(group_centers)
    if x_labels:
        ax.set_xticklabels(sorted_k)
    else:
        ax.set_xticklabels()
    return bars, group_centers