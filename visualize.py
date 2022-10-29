from typing import Optional

from matplotlib.colors import Colormap
from numpy import sqrt

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colormaps

import data
from analyze import GraphBuilder


def visualize(g: nx.Graph, *, cmap: Optional[Colormap] = None):
    # font = FontProperties(family=['sans-serif', 'Noto Color Emoji'])

    components = nx.connected_components(g)
    largest_component = max(components, key=len)
    h: nx.Graph = g.subgraph(largest_component)
    centrality = nx.betweenness_centrality(h, seed=420)

    lpc = nx.community.label_propagation_communities(h)
    community_index = {n: i for i, com in enumerate(lpc) for n in com}

    _fig, _axs = plt.subplots()
    pos = nx.spring_layout(h,
                           k=4/sqrt(len(h.nodes)),
                           seed=1337,
                           iterations=1000,
                           scale=4
                           )
    community_index['ME'] = max(community_index[n] for n in h) + 1
    node_colors = [community_index[n] for n in h]

    nx.draw_networkx(h,
                     pos=pos,
                     with_labels=True,
                     node_color=node_colors,
                     node_size=[v * 20000 for v in centrality.values()],
                     # width=0.2,
                     edge_color=[community_index[l] for (l, r) in h.edges],
                     labels=dict(g.nodes(data='name')),
                     font_size=6,
                     alpha=.9,
                     cmap=cmap,
                     edge_cmap=cmap,
                     )

    plt.show()


def _main():
    g = GraphBuilder()\
        .add(data.load_pickled("telegram.pickle"))\
        .build(usernames=True, personal_only=False)

    visualize(g, cmap=colormaps['tab10'])


if __name__ == "__main__":
    _main()
