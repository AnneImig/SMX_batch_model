#!/usr/bin/env python2
# -*- coding: utf-8 -*-



import plotly.graph_objs as go
import plotly
import plotly.io as pio
import sys
import os
import numpy as np
from PIL import ImageFont
import matplotlib.cm as cm
sys.path.append(os.getcwd())
import basic_func

script_dir = os.path.dirname(os.path.abspath(__file__))

Font= os.path.join(script_dir, 'FiraMono-Medium.otf')

#calculate timesteps and times once:
t_list = [0.0,1.0]
dt=1
t=1
for i in range(125):
    dt=dt*1.1
    t+=dt
    t_list.append(t)
t_list.append(1.8e6)

def gen_xaxis_dict(title,typ='log',rang=[-14,-9], dtick=1,showticklabels=True,showgrid=True):
    xaxis =dict(
                title=title,
                titlefont=dict(
                        size=15
                        ),
                type=typ,
                showgrid=showgrid,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=showticklabels,
                tickcolor='#000000',
                autorange=False,
                range = rang, #log
                dtick = dtick,
                tickformat="g",
                tickfont=dict(
                        size=13
                        ),
                )
    return xaxis

def gen_yaxis_dict(title,typ='log',rang=[-17,-12], dtick=1,tickformat="1.2f",ticks='outside',showticklabels=True,showgrid=True):
    yaxis =dict(
                title=title,
                titlefont=dict(
                        size=15
                        ),
                type=typ,
                showgrid=showgrid,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                
                ticks=ticks,
                showticklabels=showticklabels,
                tickcolor='#000000',
                autorange=False,
                range = rang, #log
                dtick = dtick,
                tickformat=tickformat,
                tickfont=dict(
                        size=13
                        ),
                )
    return yaxis

def saveplot_routine(fig,indv_plotname,plotdir,newfoldername,auto_open=True,pdf=True,png=True,html=True):
    #generating plot dir for semilog plots:
    os.chdir(plotdir)
    if os.path.isdir('./'+newfoldername) == False:
        os.mkdir('./'+newfoldername)
        print('directory '+newfoldername+' created')
    plotpath = os.path.join(plotdir,newfoldername)
    
    filename_html = indv_plotname + '.html'
    filename_png = indv_plotname + '.png'
    filename_pdf = indv_plotname + '.pdf'
    
    filenamepath = os.path.join(plotpath,filename_html)
    

    plotly.offline.plot(fig, filename=filenamepath, auto_open=auto_open)
    pio.write_image(fig, os.path.join(plotpath,filename_png))
    pio.write_image(fig, os.path.join(plotpath,filename_pdf))

def layout_f_plotly(xaxis,yaxis,llegendword='insert lleg w',width=850,height=850,annotations=[],fontsize=13):
    font = ImageFont.truetype(Font, fontsize)
    size = font.size
    x = 1.0- (float(size)/width + 0.15)
    y = float(size)/height + 0.05
    layout=dict(font=dict(family=Font, 
                          size=fontsize, 
                          color='#000000'),
                width=width,
                height=height,
                showlegend=True,
                plot_bgcolor='rgb(255,255,255)',
                #paper_bgcolor='rgb(155,155,155)',
                legend=dict(x=x,
                            y=y,
                            tracegroupgap=20,
                            bgcolor='rgba(255,255,255,0.8)',
                            bordercolor='rgba(0,0,0,1.0)',
                            borderwidth=1),
                dragmode='pan',
                autosize=False)
    #append axes and annotations to dict:
    layout['annotations']=annotations
    layout['xaxis']=xaxis
    layout['yaxis']=yaxis
    
    return layout


def make_scatter_traces_withconfidence(traces,x,y,y_conf,name,rgb,style='solid'):
    p_trace=go.Scatter(showlegend=True,
                        x=x,
                        y=y,
                        error_y=dict(type='data',
                                     array=np.array(y_conf)/2,
                                     color=rgb,
                                     visible=True),
                        name=name,
                        hoverinfo = 'y+name',
                        mode = 'lines+markers',
                        line=dict(color=rgb,
                                  width=2,
                                  dash = style),
                        marker=dict(size=1,
                                    opacity=0,
                                    color=rgb,
                                    ),
                        )
    traces.append(p_trace)
    return traces


def plot_sobol(df_S1,
               df_S1_conf,
               df_ST,
               df_ST_conf,
               indv_plotname,
               workingdir,
               plottitle='Global Sensitivity Analysis',
               plot_ST=True,
               plot_S1=False):
    
    #read x values = sample size which is in headers:
    x = df_S1.columns.tolist()
    del x[0:1]
    x = [float(i) for i in x]
    
    x_sorted = sorted(x)
    
    sortingindex = []
    for each in x_sorted:
        sortingindex.append(x.index(each))
        
    #get variable names:
    l_names = df_S1['names'].tolist()
    
    traces = []
    cma = cm.rainbow
    
    for index,eachname in enumerate(l_names):
        y_S1 = df_S1.loc[df_S1['names']==eachname,:].drop(df_S1.columns[[0]], axis=1).values.flatten().tolist()
        y_S1 = [y_S1[i] for i in sortingindex]
        
        y_S1_conf = df_S1_conf.loc[df_S1_conf['names']==eachname,:].drop(df_S1_conf.columns[[0]], axis=1).values.flatten().tolist()
        y_S1_conf = [y_S1_conf[i] for i in sortingindex]
        
        y_ST = df_ST.loc[df_ST['names']==eachname,:].drop(df_ST.columns[[0]], axis=1).values.flatten().tolist()
        y_ST = [y_ST[i] for i in sortingindex]
        
        y_ST_conf = df_ST_conf.loc[df_ST_conf['names']==eachname,:].drop(df_ST_conf.columns[[0]], axis=1).values.flatten().tolist()
        y_ST_conf = [y_ST_conf[i] for i in sortingindex]
        
        cn=basic_func.normalize(index,0,len(l_names)-1 )
        c = cma(cn,1)
        rgb = c[:3]
        rgb = "rgb(%s, %s, %s)" % (int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
        
        if plot_S1 == True:
            traces = make_scatter_traces_withconfidence(traces,x_sorted,y_S1,y_S1_conf,eachname+'_S1',rgb,style='dash')
        if plot_ST == True: 
            traces = make_scatter_traces_withconfidence(traces,x_sorted,y_ST,y_ST_conf,eachname+'_ST',rgb,style='solid')
    
    
    xaxis =dict(
                title='no. of samples',
                titlefont=dict(size=15),
                type='linear',
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                tickformat="g",
                tickfont=dict(size=13),
                )
    
    
    yaxis =dict(
                title='sensitivity index',
                titlefont=dict(size=15),
                type='linear',
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                tickformat="1.2f",
                tickfont=dict(size=13),
                )
    
    annotations=[]
    an = dict(x=0.50,
              y=0.95,
              showarrow=False,
              text=plottitle,
              bgcolor='rgb(255,255,255)',
              opacity=0.8,
              bordercolor='#000000',
              borderwidth=1,
              align='center',
              xref='paper',
              yref='paper',
              font =dict(family=Font, 
                         size=17, 
                         color='#000000'))
    annotations.append(an)
    
    
    layout = layout_f_plotly(xaxis,yaxis,annotations=annotations)
    
    fig1 = dict(data=traces, layout=layout)
    
    saveplot_routine(fig1,indv_plotname,workingdir,'sobol_plots')          







