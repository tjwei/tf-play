import tensorflow as tf
from graphviz import Digraph
from random import randint
from collections import defaultdict
color_table = {
    "Const": "yellow",
    "MatMul": "#bbffbb",
    "Variable": "#ffbbbb",
    "Assign": "#bbbbff"
    }


def split_name(n):
    ns = n.split('/')
    return "/".join(ns[:-1]), ns[-1]

def common_name_space(n1, n2):
    ns1 = n1.split('/')[:-1]
    ns2 = n2.split('/')[:-1]
    l = min(len(ns1), len(ns2))
    rtn = []
    for i in range(l):
        if ns1[i] != ns2[i]:
            break
        rtn.append(ns1[i])
    return "/".join(rtn)


def tfdot(graph=None):
    def get_dot_data(name_space):
        if name_space !='':
            parent, _ = split_name(name_space)
            if name_space not in dot_data_dict[parent]['subgraphs']:
                get_dot_data(parent)['subgraphs'].add(name_space)
        return dot_data_dict[name_space]

    def update_dot(name_space=''):
        name = "cluster_"+name_space if name_space else 'root'
        dot = Digraph(comment="subgraph: "+name_space, name=name)
        dot.body.append('label="%s"'%name_space)
        dot_data = dot_data_dict[name_space]
        for s in dot_data['subgraphs']:
            #print(name_space, s)
            dot.subgraph(update_dot(s))
        for node in dot_data['nodes']:
            #print(name_space, "node", node)
            dot.node(**node)
        for edge in dot_data['edges']:
            dot.edge(*edge)
        return dot


    dot_data_dict = defaultdict(lambda :{"subgraphs":set(), "edges":set(), "nodes": []})
    if graph is None:
        graph = tf.ops.get_default_graph()
    for op in graph.get_operations():
        if op.type not in color_table:
            new_color = "#%02x%02x%02x"%tuple(randint(0,100)+155 for i in range(3))
            color_table[op.type] = new_color
        color = color_table.get(op.type, "white")
        name_space, name = split_name(op.name)
        dot_data = get_dot_data(name_space)
        dot_data['nodes'].append(dict(name=op.name,  label=name, style="filled", fillcolor=color))
    
    for op in graph.get_operations():
        for ip in op.inputs:
            name_space = common_name_space(ip.op.name, op.name)
            dot_data = get_dot_data(name_space)
            dot_data['edges'].add((ip.op.name, op.name))
    return update_dot()