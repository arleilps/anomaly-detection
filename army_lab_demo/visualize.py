"""
Copyright (c) 2013, Arlei Silva
All rights reserved.
      
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
	  
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
	        
@author: Arlei Silva (arleilps@gmail.com)
"""

import sys
import getopt
import re
import math

size_picture = "10,2!"

def node_size(minimum, maximum, value):
    size = 1 + 2*float(value - minimum)/(maximum-minimum)

    return size

def edge_size(minimum, maximum, value):
    size = 1
    
    return size

def rgb_to_hex(r,g,b):
    return '#%02x%02x%02x' % (r,g,b)

def rgb(minimum, maximum, avg, value):
    m = float(maximum-minimum) / 2 
    if value > m:
        g = int(255 - 255 * float(value-m)/(maximum-m))
        r = 255
    else:
        g = 255
        r = int(255 * float(value-minimum)/(m-minimum))
 
    b = 0

    return rgb_to_hex(r, g, b)

def draw_graph(input_graph_file_name, input_data_file_name, input_centers_file_name, input_subgraph_file_name, input_residuals_file_name, output_file_name):
    output_file = open(output_file_name, 'w')
    output_file.write("graph G{\n")
    output_file.write("rankdir=\"LR\";\n")
    output_file.write("size=\""+size_picture+"\";\n")
    values = {}
    centers = {}
    subgraph = {}
    residuals = {}
    
    max_residual = -sys.float_info.max
    min_residual = sys.float_info.max
    
    residuals_file = open(input_residuals_file_name, 'r')
    for line in residuals_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        
	vertex = vec[0]
	value = float(vec[1])
	residuals[vertex] = value

	if value > max_residual:
	    max_residual = value

	if value < min_residual:
	    min_residual = value
	
    residuals_file.close()

    subgraph_file = open(input_subgraph_file_name, 'r')
    for line in subgraph_file:
        line = line.rstrip()
	
	subgraph[line] = True
    
    subgraph_file.close()

    centers_file = open(input_centers_file_name, 'r')

    for line in centers_file:
        line = line.rstrip()
	
	centers[line] = True

    centers_file.close()

    avg = 0
    max_value_node = -sys.float_info.max
    min_value_node = sys.float_info.max

    data_file = open(input_data_file_name, 'r')
    
    for line in data_file:
        line = line.rstrip()
	vec = line.rsplit(',')
        
	vertex = vec[0]
	value = float(vec[1])
	values[vertex] = value
	
        if vertex in centers:
	    avg = avg + value
    
    avg = float(avg) / len(centers)

    data_file.close()
    
    for v in values:
        if v in centers or v in subgraph:
	    if values[v] > max_value_node:
	        max_value_node = values[v]
	
            if values[v] < min_value_node:
	        min_value_node = values[v]
    
    data_file = open(input_data_file_name, 'r')

    for line in data_file:
        line = line.rstrip()
	vec = line.rsplit(',')
	
	vertex = vec[0]
	value = values[vertex]
        color = rgb(min_value_node, max_value_node, avg, value)
	size = node_size(min_value_node, max_value_node, residuals[vertex])
	if vertex in centers:
	    output_file.write(vertex+" [shape=\"square\",label=\"\",style=filled,fillcolor=\""+str(color)+"\",fixedsize=true,width="+str(size)+",height="+str(size)+"];\n")
	else:
	    if vertex in subgraph:
	        output_file.write(vertex+" [shape=\"triangle\",label=\"\",style=filled,fillcolor=\""+str(color)+"\",fixedsize=true,width="+str(size)+",height="+str(size)+"];\n")
	    else:
	        output_file.write(vertex+" [shape=\"circle\",label=\"\",style=filled,fillcolor=\""+str(color)+"\",fixedsize=true,width="+str(size)+",height="+str(size)+"];\n")
    
    data_file.close()
    
    graph_file = open(input_graph_file_name, 'r')
    max_value_edge = sys.float_info.min
    min_value_edge = sys.float_info.max
    
    for line in graph_file:
        line = line.rstrip()
	vec = line.rsplit(',')

	v_one = vec[0]
	v_two = vec[1]
	
	if v_one in values and v_two in values:
		value = float(values[v_one] + values[v_two]) / 2
	
		if value > max_value_edge:
	    		max_value_edge = value

		if value < min_value_edge:
	    		min_value_edge = value
    
    graph_file.close()
    
    graph_file = open(input_graph_file_name, 'r')
    
    for line in graph_file:
        line = line.rstrip()
	vec = line.rsplit(',')

	v_one = vec[0]
	v_two = vec[1]
	
	if v_one in values and v_two in values:
	    value = float(values[v_one] + values[v_two]) / 2
            size = edge_size(min_value_edge, max_value_edge, value)
	    color = rgb(min_value_edge, max_value_edge, avg, value)
                
	    if v_one in subgraph and v_two in subgraph:
	        output_file.write(v_one+" -- "+v_two+"[dir=\"none\",color=\""+str(color)+"\",penwidth="+str(8*size)+"];\n")
	    else:
	        output_file.write(v_one+" -- "+v_two+"[dir=\"none\",color=\""+str(color)+"\",penwidth="+str(size)+"];\n")

    graph_file.close()
    output_file.write("}")
    
    output_file.close()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    #	Parameters:
    #		- output file name	o
    #		- input graph 	g
    #		- input data	v
    #		- slice tree output s
    #

    try:
        try:
            opts, input_files = getopt.getopt(argv[1:], "o:g:v:c:h", ["output=","graph=","data=","centers=","help"])
        except getopt.error, msg:
            raise Usage(msg)
 
        output_file_name = "out"
	input_graph_file_name = "syn.graph"
	input_data_file_name = "syn.data"
	input_centers_file_name = "syn.centers"
	input_subgraph_file_name = "syn.subgraph"
	input_residuals_file_name = "comp.data"

        for opt,arg in opts:
	    if opt in ('-o', '--output'):
	        output_file_name = arg
	    if opt in ('-g', '--graph'):
	        input_graph_file_name = arg
	    if opt in ('-v', '--data'):
	        input_data_file_name = arg
	    if opt in ('-c', '--centers'):
	        input_centers_file_name = arg
	    if opt in ('-s', '--subgraph'):
	        input_subgraph_file_name = arg
	    if opt in ('-h', '--help'):
	        print "python visualize.py [-o <output_file>] [-g <graph-file>] [-v <data-file>] [-c <centers>] [-s <subgraph>]"
	        sys.exit()
      
        draw_graph(input_graph_file_name, input_data_file_name, input_centers_file_name, input_subgraph_file_name, input_residuals_file_name, output_file_name+"_graph.dot")

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
