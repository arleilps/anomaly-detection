"""
Copyright (c) 2014, Arlei Silva
All rights reserved.
      
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
	  
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
	        
@author: Arlei Silva (arleilps@gmail.com)
"""

import sys
import getopt
import math
import random
import networkx
from collections import deque

class Graph(object):
    def __init__(self, num_vertices, num_edges, num_centers, max_value, size_subgraph):
	self.num_vertices = num_vertices
	self.num_edges = num_edges
	self.num_centers = num_centers
	self.max_value = max_value
	self.centers = []
	self.size_subgraph = size_subgraph
	self.subgraph = []
    
    def set_graph(self):
	self.G =  networkx.barabasi_albert_graph(self.num_vertices, self.num_edges)
        self.edges = []
	self.values = []
        self.sp_dists = []
	
	for i in range(0, self.num_vertices):
	    self.edges.append([])
	    self.values.append(0)
	    self.sp_dists.append([])
	
	for e in self.G.edges(data=True):
	    self.edges[e[0]].append(e[1])
	    self.edges[e[1]].append(e[0])
    
    def read_graph(self, graph_input_file_name):
        self.G = networkx.Graph()
	graph_file = open(graph_input_file_name, 'r')
	vertices = {}
        self.edges = []
	self.values = []
        self.sp_dists = []
	
	for line in graph_file:
	    line = line.rstrip()
            vec = line.rsplit(',')
            
	    v1 = int(vec[0])
	    v2 = int(vec[1])

	    vertices[v1] = True
	    vertices[v2] = True
            self.G.add_edge(v1,v2)

        graph_file.close()

	self.num_vertices = len(vertices)

	for i in range(0, self.num_vertices):
	    self.edges.append([])
	    self.values.append(0)
	    self.sp_dists.append([])
        
	graph_file = open(graph_input_file_name, 'r')
	
	for line in graph_file:
	    line = line.rstrip()
            vec = line.rsplit(',')
            
	    v1 = int(vec[0])
	    v2 = int(vec[1])
	    
	    self.edges[v1].append(v2)
        
	graph_file.close()



    def set_centers(self):
        for c in range(0,self.num_centers):
            value = random.uniform(0, self.max_value)
	    center = random.randint(0,self.num_vertices-1)
	    self.values[center] = value
	    self.centers.append(center)

    def generate_subgraph(self):
        v = random.randint(0,self.num_vertices-1)
	s = networkx.cliques_containing_node(self.G, [v])

	for q in s[v]:
	    if len(q) >= self.size_subgraph:
                value = random.uniform(0, self.max_value)
	        for v in q:
		    self.values[v] = value
		self.subgraph = q
		print q
		break
    
    def compute_shortest_paths(self):
        for c in range(0,self.num_centers):
	    length=networkx.single_source_shortest_path_length(self.G,self.centers[c])
	    for v in length:
	        self.sp_dists[v].append(length[v])
    
    def compute_value(self,v):
        sum_inv_dists = 0
	value = 0
        
	if v not in self.centers:
	    for c in range(0, self.num_centers):
	        sum_inv_dists = sum_inv_dists + math.pow(math.exp(self.sp_dists[v][c]),-1)
                value = value + float(self.values[self.centers[c]]) / math.exp(self.sp_dists[v][c])
	    
	    if sum_inv_dists > 0:
	        value = float(value) / sum_inv_dists
        
	else:
	    value = self.values[v]

	return value
    
    def set_values(self):
        self.compute_shortest_paths()
        for v in range(0, self.num_vertices):
	    self.values[v] = self.compute_value(v)

    def write_values(self, output_file_name):
        output_file = open(output_file_name, 'w')
        for v in range(0, len(self.edges)):
	    output_file.write(str(v)+","+str(self.values[v])+"\n")
	     
	output_file.close() 
    
    def write_graph(self, output_file_name):
        output_file = open(output_file_name, 'w')
        for v in range(0, len(self.edges)):
	    for u in self.edges[v]:
	        if v > u:
		    output_file.write(str(v)+","+str(u)+"\n")
	     
	output_file.close() 
    
    def write_centers(self, output_file_name):
        output_file = open(output_file_name, 'w')
        for c in range(0, self.num_centers):
	    output_file.write(str(self.centers[c])+"\n")
	
	output_file.close()
    
    def write_subgraph(self, output_file_name):
        output_file = open(output_file_name, 'w')
        for c in range(0, len(self.subgraph)):
	    output_file.write(str(self.subgraph[c])+"\n")
	
	output_file.close()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg
	    
def main(argv=None):
    if argv is None:
        argv = sys.argv

    #	Parameters:
    #		- output file name	o
    #		- number of vertices v
    #		- number of edges new vertex e (preferential attachment)
    #		- number of centers	k
    #		- max value	m
    #

    try:
        try:
            opts, input_files = getopt.getopt(argv[1:], "o:v:e:k:m:s:h", ["output=","num-vertices=","num-edges=","num-centers=","max-value","size-subgraph","help"])
        except getopt.error, msg:
            raise Usage(msg)
 
        output_file_name = "syn"
	num_vertices = 100
	num_edges = 5
	num_centers = 10
	max_value = 100
	size_subgraph = 2

        for opt,arg in opts:
	    if opt in ('-o', '--output'):
	        output_file_name = arg
	    if opt in ('-v', '--num-vertices'):
	        num_vertices = int(arg)
	    if opt in ('-e', '--num-edges'):
	        num_edges = int(arg)
	    if opt in ('-k', '--num-centers'):
	        num_partitions = int(arg)
	    if opt in ('-m', '--max-value'):
	        max_value = float(arg)
	    if opt in ('-s', '--size-subgraph'):
		size_subgraph = int(arg)
	    if opt in ('-h', '--help'):
	        print "python graph_generator.py [-o <output_file>] [-v <num-vertices>] [-e <num-edges>] [-k <num-centers>] [-m <max-value>] [-s <size-subgraph>]"
	        sys.exit()
       
        g = Graph(num_vertices, num_edges, num_centers, max_value, size_subgraph)
	    
#	g.set_graph()
        g.read_graph("traffic.graph")
	g.write_graph(output_file_name + ".graph")
	g.set_centers()
	g.set_values()
	g.generate_subgraph()
        g.write_values(output_file_name + ".data")
	g.write_centers(output_file_name+ ".centers")
	g.write_subgraph(output_file_name+ ".subgraph")

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
