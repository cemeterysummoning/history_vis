from data_processing import process_main
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from pyvis.network import Network
import math
import sys
matplotlib.use('TkAgg')

def process_name(name):
    new = name
    if '.www' in name:
        new = new[4:]

    replace_dict = {
        'googleusercontent': '.googleusercontent.com',
        'obsidian': '.obsidian.md', 
        'discover': '.discover.com', 
        'sofi': '.sofi.com',
        'citi': '.citi.com',
        'freeconvert': '.freeconvert.com',
        'discord': '.discord.com'
    }

    for k, v in replace_dict.items():
        if k in new:
            new = v
    
    return new

def color(visit_type):
    visit_type = {k: math.log(v + 1) for k, v in visit_type.items()} # log of each color
    click = (202, 158, 230) # mauve
    type = (166, 209, 137) # green
    otherwise = (140, 170, 238) # blue

    total = sum(visit_type.values())

    v = (visit_type['click'] / total, visit_type['type'] / total, visit_type['otherwise'] / total)

    return '#%02x%02x%02x' % (
        int(v[0] * click[0] + v[1] * type[0] + v[2] * otherwise[0]), 
        int(v[0] * click[1] + v[1] * type[1] + v[2] * otherwise[1]), 
        int(v[0] * click[2] + v[1] * type[2] + v[2] * otherwise[2]), 
    )

def graph(places, savefile="web.html"):

    G = nx.DiGraph()

    size_scale = lambda x: x / math.sqrt(x)
    edge_scale = lambda x: x / math.sqrt(x)

    for name, data in places.items():
        if name not in G.nodes:
            interpolated_color = color(data['visit_types'])
            G.add_node(name, size=size_scale(1), color=interpolated_color)

    for name, data in places.items():
        for s_name, s_count in data['sources'].items():
            if s_name == name:
                G.nodes[name]['size'] = size_scale(s_count)
            else:
                G.add_edge(name, s_name, weight=edge_scale(s_count))

    nt = Network('1160px', '1908px', select_menu=True, bgcolor="#232634")
    nt.from_nx(G)
    nt.toggle_physics(True)
    nt.inherit_edge_colors(True)

    for node in nt.nodes:
        node['title'] = node['label']
        node['label'] = ''

    nt.save_graph(savefile)
    return nt

if __name__ == "__main__":
    path = sys.argv[1]
    places = process_main(path)
    print(places['.discord.com'])
    nt = graph(places, savefile='ace.html')
    # nt.show('ace.html')