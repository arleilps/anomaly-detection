import numpy
import scipy
import sys
from scipy.sparse import coo_matrix, identity, SparseEfficiencyWarning
from numpy import array
from scipy import linalg
import math
import operator
import getopt

SIZE_FLOAT = 8

def compute_sse_data(F):
    avg = numpy.average(F)
    sse = ((F-avg)**2).sum()

    return sse

def compute_sse_compression(F, F_app):
    return ((F-F_app)**2).sum()

def compress(lambdas, num_coeff, num_vertices, U):
    coefficients = {}
    F_app = []
    
    for i in range(0, len(lambdas)):
        coefficients[i] = numpy.absolute(lambdas[i])

    coeff_sorted = sorted(coefficients.iteritems(), key=operator.itemgetter(1), reverse=True)

    for i in range(num_coeff, len(coeff_sorted)):
        lambdas[coeff_sorted[i][0]] = 0
    
    for i in range(0, len(U)):
        F_app.append((lambdas*U[i,:]).sum())
    
    return numpy.array(F_app).real

def graph_fourier(F, U):
    lambdas = []

    for i in range(0, len(U)):
        lambdas.append(numpy.dot(F, U[:,i]))    
    
    lambdas = numpy.array(lambdas)

    return lambdas

def compute_eigenvectors(L):
    #apparently, there is not way I can compute all the eigenvectors directly from the sparse matrix.
    lamb,U = linalg.eig(L)

    return U

def read_values(input_data_name, ids):
    F = []
    input_data = open(input_data_name, 'r')

    for i in range(0, len(ids)):
        F.append(0)

    for line in input_data:
        line = line.rstrip()
        vec = line.rsplit(',')

        vertex = vec[0]
        value = float(vec[1])

        F[ids[vertex]] = value

    input_data.close()

    return numpy.array(F)    

def compute_laplacian_matrix(input_graph_name, input_data_name):
    L = []
    node_ids = {}
    ID = 0
    
    input_data = open(input_data_name, 'r')

    for line in input_data:
        line = line.rstrip()
        vec = line.rsplit(',')

        vertex = vec[0]
        
        if vertex not in node_ids:
            node_ids[vertex] = ID
            ID = ID + 1

    input_data.close()

    for i in range(0, len(node_ids)):
        L.append([])
        for j in range(0, len(node_ids)):
            L[i].append(0)

    input_graph = open(input_graph_name, 'r')
    
    for line in input_graph:
        line = line.rstrip()
        vec = line.rsplit(',')

        v_one = vec[0]
        v_two = vec[1]
        
        id_one = node_ids[vec[0]]
        id_two = node_ids[vec[1]]
        
        L[id_one][id_two] = 1
        L[id_two][id_one] = 1 
    input_graph.close()
    
    for i in range(0, len(node_ids)):
        d = 0
        for j in range(0, len(node_ids)):
            d = d + L[i][j]
            L[i][j] = -1*L[i][j]
        
        L[i][i] = d

    return numpy.array(L), node_ids       

def write_compressed(output_file_name,F):
    output_file = open(output_file_name, 'w')
    for v in range(0, len(F)):
        output_file.write(str(v)+","+str(math.fabs(F[v]))+"\n")

    output_file.close()
        
def compute_sparse_correlated_vec(F, U):
    max_score = 0
    max_u = 0
    for i in range(0, len(F)):
        score = float(numpy.dot(F, U[:,i]))/linalg.norm(U[:,i])

	if score >= max_score:
	    max_score = score
	    max_u = i
    
    print max_score
    print U[:,max_u]


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv

    #   Parameters:
    #           - output file name      o
    #           - graph g
    #           - values v
    #           - budget b
    #

    try:
        try:
            opts, input_files = getopt.getopt(argv[1:], "o:g:v:b:h", ["output=","graph=","value=","budget=","help"])
        except getopt.error, msg:
            raise Usage(msg)

        output_file_name = "comp.data"
	input_graph_name = "syn.graph"
        input_data_name = "syn.data"
	budget = 10
        
        for opt,arg in opts:
            if opt in ('-o', '--output'):
                output_file_name = arg
            if opt in ('-g', '--graph'):
                input_graph_name = arg
            if opt in ('-v', '--value'):
                input_data_name = arg
            if opt in ('-b', '--budget'):
                budget = int(arg)
            if opt in ('-h', '--help'):
                print "python graph_fourier.py [-o <output_file>] [-g <graph>] [-v <values>] [-b <budget>]"
                sys.exit()
        
        L, ids = compute_laplacian_matrix(input_graph_name, input_data_name)

        U = compute_eigenvectors(L)

        F = read_values(input_data_name, ids)

        lambdas = graph_fourier(F, U)

        num_coeff = budget

        F_app = compress(lambdas, num_coeff, len(F), U)

	write_compressed(output_file_name, F-F_app)

	V = compute_sparse_correlated_vec(F-F_app, U)

        print "F:"
        print F

        print "F_app:"
        print F_app
	print "F-F_app:"
	print F-F_app

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
                         
