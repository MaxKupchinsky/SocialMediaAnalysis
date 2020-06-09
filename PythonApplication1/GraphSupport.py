import networkx as nx
import matplotlib.pyplot as plt
from gephistreamer import graph as gephy_graph
from gephistreamer import streamer
import random
import FileManager as fm

class GraphManager:

    def __init__(self):
        self.stream = None
        self.drawn_nodes = []
        self.drawn_edges = []
        try:
            init_stream = streamer.GephiWS(hostname="localhost", port=8080, workspace="workspace1")
            self.stream = streamer.Streamer(init_stream)
        except:
            print('Соединение с сервером Gephi не было установлено. Проверьте, запущено ли приложение/ запущен ли стример')
            return


    def ClearGraphVisualisation(self):
        if self.stream != None and (self.drawn_nodes or self.drawn_edges):
            self.stream.delete_edge(*self.drawn_edges)
            self.stream.delete_node(*self.drawn_nodes)

            self.drawn_nodes = []
            self.drawn_edges = []


    def NetworxGraph(self, raw_graph_list, label_filters=['id']):       
        if type(raw_graph_list) is not list:
            raw_graph_list = [raw_graph_list]

        nx_graph = nx.Graph()
        names = []

        for raw_graph in raw_graph_list:
            tmp_nx_graph= nx.Graph()

            if 'edges' not in raw_graph or 'nodes' not in raw_graph:
                raise ValueError('На вход методу подан невалидный набор данных')
            r= random.uniform(0.4, 0.8)
            g= random.uniform(0.4, 0.8)
            b= random.uniform(0.4, 0.8)

            for node in raw_graph['nodes']:
                label=''

                if 'nodes_info' in raw_graph:
                    for filter in label_filters:
                        node_info = raw_graph['nodes_info'][node]
                        if filter in node_info:
                            label+=str(node_info[filter])+' '

                tmp_nx_graph.add_node(node, label=label, r=r, g=g, b=b)

            tmp_nx_graph.add_edges_from(raw_graph['edges'])
            names.append(raw_graph['_id'])
            graph_union = nx.compose(nx_graph,tmp_nx_graph)
            nx_graph = graph_union

        name = '+'.join(str(n) for n in names)
        nx_graph.name = name
        return nx_graph

    def SaveNgGraphToJson(self, graph, path):
        nx_graph = nx.Graph(graph)
        json = nx.node_link_data(nx_graph)

        fm.SaveJson(json, path, nx_graph.name)

    def ShowNxGraph(self, graph):
        self.ClearGraphVisualisation()

        nx_graph = nx.Graph(graph)
        nodes = list(nx_graph.nodes)
        edges = list(nx_graph.edges)

        r= nx.get_node_attributes(nx_graph,'r')
        g= nx.get_node_attributes(nx_graph,'g')
        b= nx.get_node_attributes(nx_graph,'b')
        labels= nx.get_node_attributes(nx_graph,'label')

        for node in nodes:
            self.drawn_nodes.append(gephy_graph.Node(node, size = 10, red=r[node],green=g[node], blue = b[node], label =labels[node]))
        self.stream.add_node(*self.drawn_nodes)

        for edge in edges:
            tmp_edge = gephy_graph.Edge(edge[0],edge[1], directed = False)         
            self.drawn_edges.append(tmp_edge)
        self.stream.add_edge(*self.drawn_edges)


    def ShowGraph(self, graph):
        if isinstance(graph,nx.Graph):
            self.ShowNxGraph(graph)
            return

        self.ClearGraphVisualisation()
        nodes=[]
        edges=[]
        labels=[]
        r=0.5
        g=0.5
        b=0.5
        if 'edges' not in graph or 'nodes' not in graph:
            raise ValueError('На вход методу подан невалидный набор данных')
        nodes = graph['nodes']
        edges = graph['edges']
        
        for node in nodes:
            self.drawn_nodes.append(gephy_graph.Node(node, size = 10, red=r,green=g, blue = b))
        self.stream.add_node(*self.drawn_nodes)

        for edge in edges:
            tmp_edge = gephy_graph.Edge(edge[0],edge[1], directed = False)         
            self.drawn_edges.append(tmp_edge)
        self.stream.add_edge(*self.drawn_edges)

def nxgraph(graph):
    return  nx.Graph(graph)

def DrawGraph(graph):  
    G = nx.Graph()
    G.add_edges_from(graph['edges'])
    size = round(5000/len(graph['nodes'])+1)*10
    positions=nx.kamada_kawai_layout(G)
    nx.draw(G,node_size=size, pos =positions, width=1 ,alpha=0.5,edge_color='g')  #draws the networkx graph containing nodes which are declared till before
    #nx.draw(G,node_size=10, width=1 ,alpha=0.5,edge_color='g')
    
    nx.draw_networkx_labels(G, pos=positions,labels = graph['labels'], font_size= 8)
    plt.show()  # displays the networkx graph on matplotlib canvas

def foo1(graph):
        G = nx.Graph()
        G.add_edges_from(graph['edges'])
        for node in G.nodes:
            d = G.degree(node)
        return d
