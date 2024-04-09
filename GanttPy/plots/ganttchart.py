# Copyright (c) 2022 steelpy
from __future__ import annotations
#
# Python stdlib imports
#from collections import defaultdict
#from math import isnan
import datetime
from typing import NamedTuple
from itertools import cycle

#
# package imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
##from matplotlib.patches import Patch
##import matplotlib.font_manager as font_manager
##from matplotlib.patches import ConnectionPatch
from matplotlib.lines import Line2D
#
from GanttPy.pm.manager import  get_start_end
from GanttPy.dataframe.dftime import today_floor,  get_next_monday #time_delta, to_timedelta,

#
#
class GanttChart:
    __slots__ = ['_bar_colors', '_project_list', 'pm', 'by_asset']
    
    def __init__(self, pm):
        """
        """
        self._bar_colors:list[str] = ['darkorchid', "orangered", "green", "fuchsia", "blue"]
        self.pm = pm
    #
    @property
    def bar_colors(self) -> list:
        """ """
        return self._bar_colors
    
    @bar_colors.setter
    def bar_colors(self, colors:list):
        """ colors to be used in bar plots"""
        self._bar_colors = colors
    #
    #@property
    #def project_order(self) -> list[str]:
    #    """order of project to be plotted"""
    #    #by_asset = self._df.groupby("Asset")
    #    # get groups in order 
    #    #        
    #    return self._project_list
    #
    #@project_order.setter
    #def project_order(self, projects:list[str]):
    #    """order of project to be plotted"""
    #    self._project_list = projects
    #
    def _subplots(self, by_asset, project_list):
        """ """
        # ======================================================================
        # Plot Start
        #
        number_plots = len(by_asset)
        row_no = {key:len(by_asset.get_group(key)) for key in project_list}
        size_avg = [item/number_plots for item in row_no.values()]
        #size_avg.append(len(df.Item))
        height_ratios = [round(float(item)/sum(size_avg), 2) for item in size_avg]
        number_plots += 1 # to include text
        maxavg = max(height_ratios) * 2.0
        height_ratios.append(maxavg)
        #height_ratios = None
        #fig, ax = get_subplots(rows=number_plots, column=1, height_ratios=height_ratios)
        return get_subplots(rows=number_plots, column=1, height_ratios=height_ratios)
    #
    def _get_project_list(self, df, group:dict):
        """ """
        projects = list(group.values())[0]
        by_asset = df.groupby(list(group.keys()))
        #by_asset = df.by_asset
        key_groups = by_asset.groups.keys()
        #key_groups = self.by_asset.groups.keys()
        key_groups = [key for key in key_groups]
        project_items = list(set(key_groups) - set(projects))
        asset_missing = list(set(projects)-set(key_groups))
        projects = [item for item in projects if item not in asset_missing]
        projects.extend(project_items)
        return projects
    #
    def __call__(self, project_group:dict, 
                 project_progress:list|None,
                 select_items:dict|None=None):
        """ """
        # ======================================================================
        #by_asset = self.pm.df.groupby(project_group)
        #by_asset = self.df.by_asset
        project_list = self._get_project_list(self.pm.df, group=project_group)
        #
        # ======================================================================
        mdf = self.pm.gantt_process(project_progress, select_items=select_items)
        #
        projects = list(project_group.keys())
        by_asset = mdf.groupby(projects)
        #
        # ======================================================================
        # Get color list
        #Project =  df.Asset.astype(str) + '_' + df.Project.astype(str) 
        #colors = get_color(Project, start=20)
        #c_dict = {"London_Infra":'darkorchid', "London_Proj":"orangered", 
        #          "Marine":"green", "Subsea":"cyan"}
        pick_colors = cycle(self.bar_colors)
        #
        #Project =  df.Asset.astype(str) + '_' + df.Project.astype(str)
        #df["colors"] = get_color(Project, start=20)
        #
        #
        fig, ax = self._subplots(by_asset, project_list)
        #        
        # ======================================================================
        #  Start iteration
        # ======================================================================
        #
        week_start_planned = mdf.Start_Planned
        week_start_forecast = mdf.Start_Forecast
        #week_start_planned = mdf.week_start_planned
        #week_start_forecast = mdf.week_start_forecast
        risk_end_num = mdf.risk_end_num
        #
        start_num = mdf.start_num
        end_num = mdf.end_num
        Items = mdf.Item.astype(str)
        Items = Items.tolist()
        Dependancy_Internal = mdf.Dependancy_Internal
        Dependancy_Interface = mdf.Dependancy_Interface
        #
        colors = []
        depinternal = {}
        depinterface = {}
        for i, key in enumerate(project_list):
            # get data frame group
            df2 = by_asset.get_group(key)
            #
            # =====================================================================
            # Get color list
            Project = df2.Asset.astype(str) + '_' + df2.Project.astype(str)
            color = get_color(Project, pick_colors)
            colors.extend(color[::-1])
            #
            #
            # =====================================================================
            # plot gantt planned
            task = df2.Item.astype(str)
            start = df2.Start_Planned        
            finish = df2.Finish_Planned
            plot_gantt_planned(ax[i], week_start_planned, 
                               task, start, finish, color)
            #
            # =====================================================================
            # plot gantt actual 
            progress = df2.Progress_Actual.fillna(0)
            start_forecast = df2.Start_Forecast
            finish_forecast = df2.Finish_Forecast
            plot_gantt_actual(ax[i], week_start_forecast, task, 
                              start_forecast, finish_forecast, 
                              progress, df2.Scope, color)
            #
            # =====================================================================
            # plot gantt forecast     
            plot_gantt_risk(ax[i], week_start_forecast, task, 
                            finish_forecast, df2.Finish_Risk,  
                            progress, df2.Scope, color)
            #
            # =====================================================================
            # Plot Deadlines
            milesoneDate = df2.Deadline_Date # .fillna(0)
            milesoneID = df2.Deadline_ID
            #checkxx = [isnan(item) for item in milesoneID]
            #if all([isnan(item) for item in milesoneID]):
            if milesoneID.count() > 0:
                plot_deadlines(ax[i], week_start_planned, 
                            start_forecast, finish_forecast, 
                            task, milesoneID, milesoneDate)
            #
            # =====================================================================
            # plot gantt x axis dates
            plot_gantt_dates(ax[i], key, week_start_planned, risk_end_num)
            #
            # =====================================================================
            # Connecting arrows
            # Internal
            colorID = 'dodgerblue'
            depinternal[key] = draw_arrow_between_tasks(ax[i], Items, start_num, end_num, 
                                                        task, Dependancy_Internal, 
                                                        colorID, linewidth=1.5, 
                                                        arrow_shift=2, marker_size=6)
            # Interface
            colorID = 'saddlebrown'
            depinterface[key] = draw_arrow_between_tasks(ax[i], Items, start_num, end_num, 
                                                         task, Dependancy_Interface, 
                                                         colorID)
            # =====================================================================
            # Add today line
            #
            plot_line_today(ax[i], task, week_start_planned)
        #
        #mdf['color_project'] = color
        #
        # =====================================================================
        # plot gantt x axis dates
        plot_gantt_dates(ax[i], key, week_start_planned, risk_end_num, labelbottom=True)
        #        
        # =====================================================================
        # plot conneting external arrows 
        # Internal
        colorID = 'dodgerblue'
        draw_arrow_between_plots(fig, ax, Items, by_asset, project_list, 
                                 start_num, end_num, depinternal, colorID,
                                 linewidth=1.5, arrow_shift=2, marker_size=6)
        # Interface
        colorID = 'saddlebrown'  # 'blueviolet'
        draw_arrow_between_plots(fig, ax, Items, by_asset, project_list, 
                                 start_num, end_num, depinterface, colorID)
        #
        # =====================================================================
        # Comments
        #mdf.Comments = mdf.Comments.fillna("NTR")
        #select_items = {"Project_Status":["LIVE", "PENDING", "HOLD"]} # "DELIVERED", "CANCEL"
        #name = "Project_Status"
        #drops = ["LIVE", "PENDING", "HOLD"]
        #new_df = mdf.loc[mdf[name].isin(drops)] 
        #by_asset = new_df.groupby(projects)
        ax[-1] = plot_table(ax[-1], by_asset, project_list, colors)
        #
        # =====================================================================
        # Additional progress plots
        #
        # =====================================================================

    #
    #
    def plot(self, plot_name:str, 
             project_group:dict, 
             project_progress:list|None=None,
             select_items:dict|None=None):
        """print gantt chart"""
        self.__call__(project_group=project_group,
                      project_progress=project_progress,
                      select_items=select_items)
        # Plot end
        week = datetime.date.today()
        week = week.strftime('%U-%Y')
        fgname = f"{plot_name}_Week_{week}.png"
        plt.savefig(fgname)
#
#
def get_subplots(rows:int, column:int=1, height_ratios=None):
    """ set sobplots"""
    #plt.style.use('ggplot')
    #fig = plt.figure(figsize=(16,6))
    width = 16 #/column 
    height = 5 * rows
    fig = plt.figure(figsize=(width, height))
    #fig = plt.figure()
    # Create 2x2 sub plots
    #gs = gridspec.GridSpec(2, 2)
    # row 1, span all columns
    #ax1 = fig.add_subplot(gs[0, :])
    #ax2 = fig.add_subplot(gs[1, :]) # row 1, col 0
    ##ax3 = fig.add_subplot(gs[1, 1]) # row 1, col 1
    #
    gs = gridspec.GridSpec(rows, column, #hspace=0.3,
                           height_ratios = height_ratios) # , hspace=0.5
    ax = []
    for x, item in enumerate(gs):
        if x == 0:
            ax.append(fig.add_subplot(item))
        elif (x+1) == rows:
            ax.append(fig.add_subplot(item))
        else:
            ax.append(fig.add_subplot(item, sharex=ax[x-1]))
            
        #ax2 = plt.subplot(312, sharex=ax1)
    #ax1 = fig.add_subplot(gs[0])
    #ax2 = fig.add_subplot(gs[1])
    plt.subplots_adjust(top=0.971,
                        bottom=0.006,
                        left=0.05,
                        right=0.9,
                        hspace=0.30,
                        wspace=0.2)
    return fig, ax
#
def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
    RGB color; the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)
#
# create a column with the color for each department
def get_colorX(items, colors):
    """ """
    #
    colorlist = [colors[item] for item in items[::-1]]
    return colorlist
    #
    #all_colors = [k for k,v in pltc.cnames.items()]
    #end = start + color_no
    #return [all_colors[i] for i in range(start, end, step)]
#
def get_color(project, pick_colors,
              start:int=15, step:int=1):
    """ """
    #
    #
    #items = [item for item in project]
    items = project.duplicated(keep='first')
    #citems = [next(pick_colors) for  item in items if not item]
    items = [project.iloc[x] for x, item in enumerate(items) if not item]
    #rate = ceil(len(items) / len(pick_colors))
    #
    #all_colors = list(set([k for k,v in pltc.cnames.items()]))
    #end = start + len(items)
    #set_color = [all_colors[i] for i in range(start, end, step)]
    #set_color = [choice(all_colors) for i in range(start, end, step)]
    #set_color = pick_colors * rate
    #col_dic = {item : set_color[x] for x, item in enumerate(items)}
    col_dic = {item : next(pick_colors) for item in items}
    #end = start + len(project)
    colist =  [col_dic[iitem] for iitem in project]
    return colist[::-1]
    #return [col_dic[iitem] for iitem in project[::-1]]
#
#
class Dependency(NamedTuple):
    """ """
    successor:int|str
    predecessors:list
#    #end_risks:list
#
def draw_arrow_between_tasks(ax, Indices, start_num, end_num, 
                             tasks, dependancy, 
                             color:str="black", linewidth:float=1,
                             arrow_shift:float=1, marker_size:float=4,
                             head_width:float=0.25, head_length:float=2):
    """ """
    #dependency = defaultdict(list)
    dependency = {}
    #
    #Indices = Index.tolist()
    #indices = tasks.tolist()
    indxrev = tasks.tolist()
    indxrev.reverse()
    #steps = len(tasks) - 1
    #for idx in range(steps, -1, -1):
    for idx, key, in enumerate(tasks[::-1]):
        index = Indices.index(str(key))
        row = dependancy.iloc[index]
        try:
            items = [int(row)]
        except ValueError:
            items = row.strip()
            items = items.split(',')
            items = [item for item in items]        
        if items[0]:
            for item in items:
                pre_index = Indices.index(str(item))
                task_days = end_num.iloc[pre_index]
                x = [task_days]                
                #
                try:
                    predecessor = indxrev.index(str(item))
                except ValueError:
                    #print(f'dependency missing {item}')
                    try:
                        items2 = row.split(',')
                    except AttributeError:
                        items2 = [row]
                    #dependency[key].extend([int(i) for i in items2])
                    dependency[key] = Dependency(successor=key,
                                                 predecessors=[int(i) for i in items2])
                    continue
                #
                y = [predecessor]
                #
                ax.plot(x, y, 'o', color=color, ms=marker_size)
                #
                x.append(x[-1])
                #successor = steps - idx
                successor =  idx
                y.append(successor)
                #
                #task2_idx = Index.loc[pre_index]
                task2_days = start_num.iloc[index]
                x.append(task2_days)
                y.append(y[-1])
                #
                ax.plot(x,y, '-.', 
                        color=color, linewidth=linewidth,
                        dash_capstyle='round')
                #
                ax.arrow(x[-1]-arrow_shift, y[-1], 1, 0,
                         head_width=head_width, head_length=head_length, 
                         linewidth=linewidth, color=color)
    #
    ax.set_xlim([start_num.min(), end_num.max()+7])
    #ax.set_ylim([ymin, ymax])    
    #fig.autofmt_xdate()
    #plt.tight_layout()
    #plt.show()
    #print('---')
    return dependency
#
def draw_arrow_between_plots(fig, ax, indices, by_asset, assets_list, 
                             start_num, end_num, dependancy,
                             color:str="black", linewidth:float=1,
                             arrow_shift:float=1, marker_size:float=4,
                             head_width:float=0.25, head_length:float=2):
    """ """
    #plot_no = assets_list[::-1]
    #plot_no.insert(0, "Table")
    yconn = []
    xconn = []
    transFigure = fig.transFigure.inverted()
    #indices = Index.tolist()
    for key, succesors in dependancy.items():
        df2 = by_asset.get_group(key)
        #
        x1 = assets_list.index(key)
        bbox = ax[x1].get_position()
        yconn.extend([bbox.y1, bbox.y0])
        xconn.extend([bbox.x1, bbox.x0])
        #
        task = df2.Item[::-1].astype(str) # reversed for fig position
        task = task.tolist()
        for successor, item in succesors.items():
            idx = indices.index(str(successor))
            coord1x = start_num.iloc[idx]
            coord1y = task.index(str(successor))
            coord1 = transFigure.transform(ax[x1].transData.transform([coord1x, coord1y]))
            #
            for predecessor in item.predecessors:
                idx2 = indices.index(str(predecessor))
                coord2x = end_num.iloc[idx2]
                #for x2 in range(1, len(plot_no)):
                #    print(x2)
                #    asset = plot_no[x2]
                for x2, asset in enumerate(assets_list):
                    if asset == key:
                        continue
                    #
                    df3 = by_asset.get_group(asset)
                    task2 = df3.Item[::-1].astype(str)
                    task2 = task2.tolist()
                    try:
                        coord2y = task2.index(str(predecessor))
                        coord2 = transFigure.transform(ax[x2].transData.transform([coord2x, coord2y]))
                    except ValueError:
                        continue
                    # add mid point 
                    coord3 = transFigure.transform(ax[x1].transData.transform([coord2x, coord1y]))
                    #
                    # add a vertical dashed line
                    line1 = Line2D((coord2[0], coord3[0]), (coord2[1], coord3[1]),
                                    transform=fig.transFigure, 
                                    ls='-.', color=color,
                                    linewidth=linewidth,
                                    dash_capstyle='round')
                    #
                    #line1 = Line2D((coord1[0], coord1[1]), (coord3[0], coord3[1]),
                    #                transform=fig.transFigure, 
                    #                ls='-.', color=color, 
                    #                linewidth=linewidth,
                    #                dash_capstyle='round')
                    #
                    line2 = Line2D((coord3[0], coord1[0]), (coord3[1], coord1[1]),
                                    transform=fig.transFigure, 
                                    ls='-.', color=color, 
                                    linewidth=linewidth,
                                    dash_capstyle='round')
                    #
                    ax[x2].plot(coord2x, coord2y, 'o', color=color, ms=marker_size) # predecesor
                    #color = 'pink'
                    ax[x1].arrow(coord1x - arrow_shift, coord1y, 1, 0,
                                 head_width=head_width, head_length=head_length, 
                                 linewidth=linewidth, color=color)
                    #ax[x1].plot(coord1x, coord1y, 'o', color=color, ms=10) # susscesor
                    #
                    fig.lines.extend([line1, line2])
                    #fig.lines.extend([line1, line2])
                    break
    #print('---')
#
#def get_cmap(n, name='hsv'):
#    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
#    RGB color; the keyword argument name must be a standard mpl colormap name.'''
#    return plt.cm.get_cmap(name, n)
#
#
#
def get_bar_data(task, start_num, days_start_to_end):
    """conver to list"""
    coord = task.iloc[::-1].tolist()
    width = days_start_to_end.iloc[::-1].tolist()
    left = start_num.iloc[::-1].tolist()
    coord.append("Milestone")
    width.append(0)
    left.append(0)
    return coord, width, left
#
#
def plot_gantt_planned(ax, week_start, task, start, finish, color):
    """ """
    start_num, end_num, days_start_to_end = get_start_end(week_start, start, finish)
    coord, width, left = get_bar_data(task, start_num, days_start_to_end)
    #
    ax.barh(coord, width=width, left=left, 
            height=0.90, align="center", 
            edgecolor='black', linewidth=1.5,
            color=color, alpha=0.2)
    #
    for label in ax.get_yticklabels(which='major'):
        #label.set(rotation=30, horizontalalignment='right')
        label.set_fontname('Consolas')
        label.set_fontsize(8)
    #
    #return ax
#
def plot_gantt_actual(ax, week_start, task, start, finish, progress,
                      scope, color):
    """ """
    #
    start_num, end_num, days_start_to_end = get_start_end(week_start, start, finish)
    coord, width, left = get_bar_data(task, start_num, days_start_to_end)
    # bar plot 
    ax.barh(coord, width=width, left=left, 
            height=0.60,
            #edgecolor='black', linewidth=1.0,
            color=color, alpha=0.50)    
    #
    # days between start and current progression of each task
    #current_num = (days_start_to_end * progress/100)
    current_width = (days_start_to_end * progress/100)
    current_width = current_width.iloc[::-1].tolist()
    current_width.append(0)
    # bars plot progress
    ax.barh(coord, width=current_width, left=left, 
            height=0.60, color=color)
    #
    # Plot progress and task name
    #steps = len(color) - 1
    #for idx in range(steps, -1, -1):
    #    ax.text(end_num.iloc[idx] + 2.0, steps-idx, 
    #            f"{int(progress.iloc[idx])}% [{scope.iloc[idx]}]",
    #            #f"{int(progress.iloc[idx])}%", 
    #            va='center', alpha=1.0, fontsize=8)
    #    
    #
    #return ax
#
#
def plot_gantt_risk(ax, week_start, task, start, finish, 
                    progress, scope, color):
    """ """
    #nett_progress = progress_forecast - progress
    #
    start_num, end_num, days_start_to_end = get_start_end(week_start, start, finish)
    coord, width, left = get_bar_data(task, start_num, days_start_to_end)    
    #
    # bar plot 
    ax.barh(coord, width=width, left=left, 
            height = 0.60, 
            linestyle ="--", hatch="////",
            edgecolor=color, linewidth=1.0,
            color=color, alpha=0.25)
            #edgecolor=color, linewidth=2.0,
            #color=color, alpha=0.10)     
    #
    # Plot progress and task name
    steps = len(color) - 1
    for idx in range(steps, -1, -1):
        ax.text(end_num.iloc[idx] + 2.0, steps-idx, 
                f"{int(progress.iloc[idx])}% [{scope.iloc[idx]}]",
                #f"{int(progress.iloc[idx])}%", 
                va='center', alpha=1.0, fontsize=8)
        
    #    
#
#
#
def plot_deadlines(ax, week_start, start, finish, task,
                    milesoneID, milesoneDate):
    """ """
    # Basic calcs
    start_num, end_num, days_start_to_end = get_start_end(week_start, start, finish)
    coord, width, left = get_bar_data(task, start_num, days_start_to_end)    
    # number of days from project start to end of tasks
    proj_start = week_start.min()
    proj_end = milesoneDate
    end_ms = (proj_end - proj_start).dt.days
    end_ms = end_ms.fillna(0)
    idy = len(coord) - 1
    #
    taskend = end_num.iloc[::-1].tolist()
    leyend = milesoneID.iloc[::-1].tolist()
    #
    for idx, row in enumerate(end_ms[::-1]):
        if row:
            ax.plot([row], [idy], marker="D", 
                    ms=8, mew=1, mec="blue", mfc="red")
            ax.text(row+2, idy+0.2, leyend[idx],
                    fontfamily="Consolas", fontweight="bold", color="b", fontsize=8)
            ax.axvline(x=row, color='red', linewidth=1, linestyle="--")
            # Check if task is late
            if taskend[idx] > row :
                #ax.text(taskend[idx]+1, idx+0.2, "!", color="red",
                ax.text(row+1, idx+0.2, "!", color="red", 
                        fontfamily="Calibri", fontweight="bold", 
                        fontsize=13) # fontstyle="italic", 
    #
    #print('---')
    return ax
    
#
def plot_line_today(ax, task, week_start):
    """ """
    from pandas import Timestamp
    #week_start = start.dt.to_period('W').dt.start_time
    #print(week_start)
    #proj_start = week_start.min()
    #today = Timestamp.today().floor('D')
    today = today_floor()
    today = (today - week_start.min()).days
    #
    #ax.plot([today, today], [0, len(task)],
    #         color='black', linewidth=1.5, linestyle="-")  # 'deeppink'   
    #
    #ax.legend("##", bbox_to_anchor=(today, len(task)))
    ax.axvline(x=today, color='black', linewidth=1.5, linestyle="-")
    #
    week = Timestamp.today()
    week = week.strftime('%U') # -%Y
    idy = len(task)
    ax.text(today+2, idy+0.50, f"Week:{week}", color="black",
            fontfamily="Consolas",  fontsize=8,  fontweight="bold",)
    #
    return ax
#
def plot_gantt_leyend(ax, c_dict):
    """ """
    #c_dict = {"Today":'deeppink', "Interface":"orangered", "Internal":"dodgerblue"}
    legend_elements = [Patch(facecolor=c_dict[i], label=f"{i}")  
                       for x, i in enumerate(c_dict)]
    #
    font = font_manager.FontProperties(family='Consolas',
                                       #weight='bold',
                                       style='normal', size=8)
    #
    ax.legend(handles=legend_elements,
               loc='upper right', prop=font, frameon=False,
               fancybox=False, shadow=False, ncol=1) #bbox_to_anchor=(-0.2, -0.1),
    #ax.set_title('Comments', loc='left', #y=0.85, x=0.02,
    #             fontsize=10, fontname ='Consolas') 
    #ax.set_axis_off()
    return ax
#
def plot_gantt_dates(ax, title, week_start, end_num, labelbottom=False):
    """ """
    #-----TICKS --------
    from pandas import Timedelta, date_range
    #
    tot_num = 7 + (int(np.ceil(end_num.max()/7)) * 7)
    td = Timedelta(tot_num, "d")
    total_end = week_start.min() + td
    #xticks = np.arange(0, end_num.max()+1, 7)
    xticks_labels = date_range(week_start.min(), 
                               end=total_end).strftime("%d/%m/%y")
    #
    #xticks_minor = np.arange(0, end_num.max()+1, 1)
    xticks = np.arange(0, tot_num+7, 7)
    xticks_minor = np.arange(0, tot_num+7, 1)
    #
    ax.set_xticks(xticks)
    ax.set_xticks(xticks_minor, minor=True)
    ax.set_xticklabels(xticks_labels[::7])
    #  
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')
        label.set_fontname('Consolas')
        label.set_fontsize(8)
    #
    ax.set_title(title, loc='left',
                 fontfamily="Calibri", fontweight="bold",
                 color="forestgreen", fontsize=16)  #  y=0.85, x=0.02, # midnightblue
    #
    #plot_gantt_leyend(ax)
    #
    ax.grid(color='gainsboro', linestyle='-')
    ax.set_axisbelow(True)
    #
    #ax.tick_params('x', labelbottom=labelbottom)
    #
    return ax
#
def plot_leyend(ax, project, task, comment, contractor, 
                department, milestoneID, color):
    """ """
    1/0
    #----- LEGENDS ------
    comm = comment[::-1]
    colist = color[::-1]
    #
    max_proj = max([len(item) for item in project])
    max_title = max([len(item) for item in department])
    max_cont = max([len(item) for item in contractor])
    milestone = milestoneID.fillna("-")
    max_mil = max([len(item) for item in milestone])
    #
    
    #
    c_dict = {item:colist[i] for i, item in enumerate(task[::-1])}
    legend_elements = [Patch(facecolor=c_dict[i], 
                             label=f"{task.iloc[x]:<4}- Project: {project.iloc[x]:<{max_proj}} Department: {department.iloc[x]:<{max_title}}, Provider: {contractor.iloc[x]:<{max_cont}}, Milestone: {milestone.iloc[x]:<{max_mil}}, Note: {comm[x]}")  
                       for x, i in enumerate(c_dict)]
    #
    font = font_manager.FontProperties(family='Consolas',
                                       #weight='bold',
                                       style='normal', size=8)
    #
    ax.legend(handles=legend_elements,
               loc='center left', prop=font, frameon=False,
               fancybox=True, shadow=False, ncol=1) #bbox_to_anchor=(-0.2, -0.1),
    #ax.set_title('Comments', loc='left', #y=0.85, x=0.02,
    #             fontsize=10, fontname ='Consolas') 
    ax.set_axis_off()
    return ax
#
def plot_table(ax, df_bylist, assets_list, color_list):
    """ """
    #
    columns = ('Task', 'Resource', 'Status', 'Comment')
    #
    new_color = []
    rows = []
    cell_text = []
    #colors = []
    scope_lenght = [len(columns[0])]
    contractor_lenght = [len(columns[1])]
    status_lenght = [len(columns[2])]
    comm_lenght = [len(columns[3])]
    heading = ["Scope", "Contractor", "Project_Status", "Comments"]
    for i, key in enumerate(assets_list):
        df2 = df_bylist.get_group(key)
        #
        project = df2.Asset.astype(str) + '_' + df2.Project.astype(str)
        items = project.duplicated(keep='first')
        rows.extend([f"{df2.Item.iloc[idx]} - {project.iloc[idx]}" if not item else f"{df2.Item.iloc[idx]} -" 
                     for idx, item in enumerate(items)])
        #
        #rows.extend([f"{item} - {df2.Asset.iloc[idx]} {df2.Project.iloc[idx]}" 
        #             for idx, item in enumerate(df2.Item)])
        data = df2[heading].values.tolist() # "Asset", "Project", 
        cell_text.extend(data)
        #
        comms = df2.Comments
        #
        scope_lenght.append(max([len(item) for item in df2.Scope]))
        contractor_lenght.append(max([len(item) for item in df2.Contractor]))
        status_lenght.append(max([len(item) for item in df2.Project_Status]))
        comm_lenght.append(max([len(item) for item in df2.Comments]))
        #
        #new_color.append(color_list[i])
    #
    #
    #ax.patch.set_visible(False)
    ax.axis('tight')
    ax.axis('off')
    #
    colwdth = [1/(len(columns) + 1)]
    colwdth = [max(scope_lenght), max(contractor_lenght), 
               max(status_lenght), max(comm_lenght), 
               max([len(item) for item in rows])]
    nocol = len(colwdth)
    colwdth = [item/nocol for item in colwdth]
    colratios = [round(float(item)/sum(colwdth), 3) for item in colwdth]
    #
    #ax.rcParams['font.family'] = 'Consolas'
    # Add a table at the bottom of the axes
    table = ax.table(cellText=cell_text,
                     rowLabels=rows,
                     rowColours=color_list,
                     colLabels=columns,
                     #colWidths=colwdth * len(columns),
                     colWidths=colratios,
                     loc='upper right')
                     #edgecolor="lightsteelblue")
                     #ls="--")
    #
    cellDict = table.get_celld()
    for i in range(0, len(columns)):
    #    cellDict[(0,i)].set_height(.10)
        for j in range(0, len(color_list)+1):
            cellDict[(j,i)].fontsize = 8
            cellDict[(j,i)].linewidth=1
            cellDict[(j,i)].linestyle="--"
            cellDict[(j,i)].set_text_props(fontfamily="Consolas")
            cellDict[(j,i)].edgecolor = "lightsteelblue"
    #        cellDict[(j,i)].set_height(.05)    
    #
    #for r in range(0, len(columns)):
    #    cell = table[0, r]
    #    cell.set_height(0.10)
    #
    table.auto_set_font_size(False)
    #table.set_fontsize(10)
    table.scale(1, 1.5)
    #
    #
    return ax
#
def plot_acc_progress(ax):
    """ """
    #fig2, ax2 = plt.subplots(2, 2)
    ax.plot([0, 1, 2, 3], [3, 8, 1, 10])
    #
    ax.grid(color='whitesmoke', linestyle='-')
    ax.set_axisbelow(True)
    return ax
#
#