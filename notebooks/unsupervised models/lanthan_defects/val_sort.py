import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from algorithms import pca_algo, kmeans_algo, nmf_algo, tsne_algo

def sort_clusterlabels_phase(df_kmeans, n_clusters):
    df_times = df_kmeans.groupby(["labels", "cluster"]).size().reset_index(name="Time")
    
    if(n_clusters == 5):
        unknown_df = df_times[df_times['labels'].str.match('unknown')]
        unk_newlabel = unknown_df.loc[unknown_df['Time'] == unknown_df.Time.max(), 'cluster'].values[0]
        df_kmeans = df_kmeans.replace({'unknown': unk_newlabel})

    m_df = df_times[df_times['labels'].str.match('m')]
    po_df = df_times[df_times['labels'].str.match('p-o')]
    o_df = df_times[df_times['labels'].str.match('o')]
    t_df = df_times[df_times['labels'].str.match('t')]
    
    
    m_newlabel = m_df.loc[m_df['Time'] == m_df.Time.max(), 'cluster'].values[0]
    po_newlabel = po_df.loc[po_df['Time'] == po_df.Time.max(), 'cluster'].values[0]
    o_newlabel = o_df.loc[o_df['Time'] == o_df.Time.max(), 'cluster'].values[0]
    t_newlabel = t_df.loc[t_df['Time'] == t_df.Time.max(), 'cluster'].values[0]
    
    df_kmeans = df_kmeans.replace({'m': m_newlabel,
                                   'p-o': po_newlabel,
                                   'o': o_newlabel, 
                                   't':t_newlabel })
    return df_kmeans



def sort_clusterlabels_defects(df_kmeans, n_clusters):
    df_times = df_kmeans.groupby(["labels", "cluster"]).size().reset_index(name="Time")

    La2_df = df_times[df_times['labels'].str.match('2La')]
    LaV_df = df_times[df_times['labels'].str.match('LaV')]
    inter_df = df_times[df_times['labels'].str.match('inter')]
    La2V_df = df_times[df_times['labels'].str.match('La2V')]
    
    
    La2_newlabel = La2_df.loc[La2_df['Time'] == La2_df.Time.max(), 'cluster'].values[0]
    LaV_newlabel = LaV_df.loc[LaV_df['Time'] == LaV_df.Time.max(), 'cluster'].values[0]
    inter_newlabel = inter_df.loc[inter_df['Time'] == inter_df.Time.max(), 'cluster'].values[0]
    La2V_newlabel = La2V_df.loc[La2V_df['Time'] == La2V_df.Time.max(), 'cluster'].values[0]
    
    df_kmeans = df_kmeans.replace({'2La': La2_newlabel,
                                   'LaV': LaV_newlabel,
                                   'inter': inter_newlabel, 
                                   'La2V':La2V_newlabel })
    return df_kmeans

def name_change(df):
    # change names for plotly bib
    df3 = df.iloc[:, [0, 1, 2]].copy()
    df3 = df.rename(columns={0: 'x1', 1: 'x2', 2:'x3'})
    df3['cluster'] = df[['cluster']]
    df3['labels'] = df[['labels']] 
    return df3

def plot2d(df3, title, clus_lab):
    lm = sns.lmplot(data=df3, x='x1', y='x2',hue=clus_lab, fit_reg=False, legend=True, legend_out=True)
    fig = lm.fig 
    fig.suptitle(title, fontsize=10)

def plot3d(df3, title, clus_lab):
    fig = px.scatter_3d(
    df3, x='x1', y='x2', z='x3', color=df3[clus_lab],
    labels={'x1': 'C 1', 'x2': 'C 2', 'x3': 'C 3'}, title=title)
    fig.show()

def hyperparameter_testing(X, reduction_methode, hyperpar, labels_true, keyword, n_clusters):
    # Hyperparameter PCA component test
    # select pca, nmf, tsne
    performance = []
    i = 1
    for par in hyperpar: 
        if(reduction_methode == 'pca'):
            df = pca_algo(X, par)
        elif(reduction_methode == 'nmf'):
            df = nmf_algo(X, par)
        elif(reduction_methode == 'tsne'):
            df = tsne_algo(X, par)
            
        df_kmeans = kmeans_algo(df, n_clusters)
        df_kmeans['labels'] = labels_true
        if(keyword == 'phase'):
            df_kmeans = sort_clusterlabels_phase(df_kmeans, n_clusters)
        elif(keyword == 'defects'):
            df_kmeans = sort_clusterlabels_defects(df_kmeans, n_clusters)
        acc = accuracy_score(df_kmeans['labels'], df_kmeans['cluster'])
        performance.append(acc)
        print("Round: " + str(i))
        i = i + 1

    perf_dic = dict(zip(hyperpar, performance))
    print('Best value of performance: ' + str(max(perf_dic.values())) + ' Hyperparameter = ' + str(max(perf_dic, key=perf_dic.get)))
    print('Overview: ' + str(perf_dic))
