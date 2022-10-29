import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

import data
from analyze import GraphBuilder

kind_colors = {
    'me': 'red',
    'contact': 'steelblue',
    'community': 'salmon',
    'default': 'white'
}

edge_colors = {
    'personal': '#7142cf',
    'other': '#aaa'
}


def visualize(g: nx.Graph):
    font = FontProperties(family=['sans-serif', 'Noto Color Emoji'])

    components = nx.connected_components(g)
    largest_component = max(components, key=len)
    h = g.subgraph(largest_component)
    centrality = nx.betweenness_centrality(h)

    lpc = nx.community.label_propagation_communities(h)
    community_index = {n: i for i, com in enumerate(lpc) for n in com}

    fig, axs = plt.subplots()
    pos = nx.spring_layout(h, k=0.15, seed=1337, iterations=1000, scale=4)

    nx.draw_networkx(g,
                     pos=pos,
                     with_labels=True,
                     node_color=[community_index[n] for n in h],
                     node_size=[v * 20000 for v in centrality.values()],
                     # width=0.2,
                     edge_color='gainsboro',
                     labels=dict(g.nodes(data='name')),
                     font_size=8
                     )

    plt.show()


def _main():
    builder = GraphBuilder()
    builder.add(data.load_pickled("telegram.pickle"))
    g = builder.build()

    visualize(g)


if __name__ == "__main__":
    _main()
