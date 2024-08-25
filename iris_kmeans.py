# %%
import numpy as np
import panel as pn
import hvplot.pandas

from sklearn.cluster import KMeans
from bokeh.sampledata import iris
pn.extension()

# %% [markdown]
# This app provides an example of building a simple dashboard using Panel. It demonstrates how to take the output of  k-means clustering on the Iris dataset (performed using scikit-learn), parameterizing the number of clusters and the x and y variables to plot. The entire clustering and plotting pipeline is expressed as a single reactive function that returns a plot that responsively updates when one of the widgets changes.

# %%
flowers = iris.flowers.copy()
cols = list(flowers.columns)[:-1]

x = pn.widgets.Select(name='x', options=cols)
y = pn.widgets.Select(name='y', options=cols, value='sepal_width')
n_clusters = pn.widgets.IntSlider(name='n_clusters', start=1, end=5, value=3)

@pn.depends(x.param.value, y.param.value, n_clusters.param.value)
def get_clusters(x, y, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters)
    est = kmeans.fit(iris.flowers.iloc[:, :-1].values)
    flowers['labels'] = est.labels_.astype('str')
    centers = flowers.groupby('labels').mean()
    return (flowers.sort_values('labels').hvplot.scatter(x, y, c='labels') *
            centers.hvplot.scatter(x, y, marker='x', color='black', size=200,
                                   padding=0.1, line_width=5))

pn.Column(
    '# Iris K-Means Clustering',
    pn.Row(pn.WidgetBox(x, y, n_clusters), get_clusters)
).servable()


