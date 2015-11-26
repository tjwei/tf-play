from graphviz import Digraph
import tensorflow as tf
from random import randint
color_table = {
    "Const": "yellow",
    "MatMul": "#bbffbb",
    "Variable": "#ffbbbb",
    "Assign": "#bbbbff"
    }

def tfdot(graph=None):
    if graph is None:
        graph = tf.ops.get_default_graph()
    dot = Digraph(comment="node graph")
    for op in graph.get_operations():
        if op.type not in color_table:
            new_color = "#%02x%02x%02x"%tuple(randint(0,100)+155 for i in range(3))
            color_table[op.type] = new_color
        color = color_table.get(op.type, "white")
        dot.node(op.name,  op.name, style="filled", fillcolor=color)
    for op in graph.get_operations():
        for ip in op.inputs:
            dot.edge(ip.op.name, op.name )
    return dot