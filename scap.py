# the program takes a file that describes a circuit
# using the netlist format, and then use MNA to solve it.

# netlist format:
# 1. Resistor: R<name> <node1> <node2> <resistance>
# 2. Capacitor: C<name> <node1> <node2> <capacitance>
# 3. Inductor: L<name> <node1> <node2> <inductance>
# 4. Voltage source: V<name> <node1> <node2> <voltage>
# 5. Current source: I<name> <node1> <node2> <current>
# 6. Op Amp: O<name> <node1> <node2> <node3>
# 7. Voltage Control Voltage source: E<name> <node+> <node-> <nodeC+> <nodeC-> <gain>
# 8. Current Control Voltage source: H<name> <node+> <node-> <nodeC> <gain>
# 9. Voltage Control Current source: G<name> <node+> <node-> <nodeC+> <nodeC-> <gain>
# 10. Current Control Current source: F<name> <node+> <node-> <nodeC> <gain>

# use the term 'Symbolic' if the value of the component is unknown


import sympy as sp
import time


def scam(fname):
    start_time = time.time()
    # read the file
    f = open(fname, 'r')
    lines = f.readlines()
    
    N = 0   # number of nodes
    M = 0   # number of voltage sources
    l_M = []   # name of voltage sources
    d_M = {}   # dictionary of voltage sources

    print('Netlist:')
    # get the number of nodes and voltage sources
    for line in lines:
        print(line, end='')
        # parse the line
        line = line.split()
        # get the type of the component
        component_type = line[0][0]
        if component_type in ['V', 'E', 'H', 'O']:
            l_M.append(line[0])
            d_M[line[0]] = M
            M += 1
        node1, node2 = line[1], line[2]
        N = max(N, int(node1), int(node2))

    print()
    print()
    # print('Number of nodes: ', N)
    # print('Number of voltage sources: ', M)
    # print()

    # initialize the matrices
    G = sp.zeros(N, N)   # conductance matrix
    B = sp.zeros(N, M)   # voltage source matrix 1
    C = sp.zeros(M, N)   # voltage source matrix 2
    D = sp.zeros(M, M)   # controlled source matrix
    z = sp.zeros(N+M, 1)
    s = sp.symbols('s')  # laplace variable
    M_ = 0               # number of controlled sources
    for line in lines:
        # parse the line
        line = line.split()
        component_type = line[0][0]
        name = line[0]
        node1 = int(line[1])
        node2 = int(line[2])
        index1 = node1 - 1
        index2 = node2 - 1

        if component_type == 'R':
            # resistor
            resistance = line[3]
            resistance = sp.symbols(name)
            
            # if connected to ground
            if node1 == 0:
                G[index2, index2] += 1/resistance
                continue
            if node2 == 0:
                G[index1, index1] += 1/resistance
                continue

            # add the resistor to the circuit
            G[index1, index1] += 1/resistance
            G[index2, index2] += 1/resistance

            G[index1, index2] -= 1/resistance
            G[index2, index1] -= 1/resistance
            
        if component_type == 'C':
            # capacitor
            capacitance = line[3]

            capacitance = sp.symbols(name)

            # if connected to ground
            if node1 == 0:
                G[index2, index2] += capacitance * s
                continue
            if node2 == 0:
                G[index1, index1] += capacitance * s
                continue
            # add the capacitor to the circuit
            G[index1, index1] += s * capacitance
            G[index2, index2] += s * capacitance
            G[index1, index2] -= s * capacitance
            G[index2, index1] -= s * capacitance
        
        if component_type == 'L':
            # inductor
            inductance = line[3]

            inductance = sp.symbols(name)
            # if connected to ground
            if node1 == 0:
                G[index2, index2] += 1/(s * inductance)
                continue
            if node2 == 0:
                G[index1, index1] += 1/(s * inductance)
                continue
            # add the inductor to the circuit
            G[index1, index1] += 1/(s * inductance)
            G[index2, index2] += 1/(s * inductance)
            G[index1, index2] -= 1/(s * inductance)
            G[index2, index1] -= 1/(s * inductance)
        
        if component_type == 'V':
            # voltage source
            
            voltage = sp.symbols(name)
            
            # print(index1, index2)
            # print(node1, node2)
            z[N+M_] = voltage
            # if connected to ground
            if node1 == 0:
                B[index2, M_] = -1
                C[M_, index2] = -1
                M_ += 1
                continue
            if node2 == 0:
                B[index1, M_] = 1
                C[M_, index1] = 1
                M_ += 1
                continue

            B[index1, M_] = 1
            B[index2, M_] = -1
            C[M_, index1] = 1
            C[M_, index2] = -1
            
            M_ += 1
        
        if component_type == 'E':
            # voltage controlled voltage source
            
            nodeC1 = int(line[3])
            nodeC2 = int(line[4])
            indexC1 = nodeC1 - 1
            indexC2 = nodeC2 - 1

            gain = sp.symbols(name)

            C[M_, indexC1] += -gain
            C[M_, indexC2] += gain

            z[N+M_] = 0
            # if connected to ground
            if node1 == 0:
                B[index2, M_] += -1
                C[M_, index2] += -1
                M_ += 1
                continue
            if node2 == 0:
                B[index1, M_] += 1
                C[M_, index1] += 1
                M_ += 1
                continue

            B[index1, M_] += 1
            B[index2, M_] += -1
            C[M_, index1] += 1
            C[M_, index2] += -1
            
            M_ += 1

        if component_type == 'G':
            # voltage controlled current source
            
            nodeC1 = int(line[3])
            nodeC2 = int(line[4])
            indexC1 = nodeC1 - 1
            indexC2 = nodeC2 - 1

            gain = sp.symbols(name)

            # if connected to ground
            if node1 == 0:
                G[index2, indexC1] -= gain
                G[index2, indexC2] += gain
                continue
            if node2 == 0:
                G[index1, indexC1] += gain
                G[index1, indexC2] -= gain
                continue
            
            G[index1, indexC1] += gain
            G[index1, indexC2] -= gain
            G[index2, indexC1] -= gain
            G[index2, indexC2] += gain

        if component_type == 'H':
            # current controlled voltage source
            
            nodeC = line[3]

            gain = sp.symbols(name)

            z[N+M_] = 0
            D[M_, d_M[nodeC]] -= gain
            # if connected to ground
            if node1 == 0:
                B[index2, M_] += -1
                C[M_, index2] += -1
                M_ += 1
                continue
            if node2 == 0:
                B[index1, M_] += 1
                C[M_, index1] += 1
                M_ += 1
                continue

            B[index1, M_] += 1
            B[index2, M_] += -1
            C[M_, index1] += 1
            C[M_, index2] += -1
            
            M_ += 1
        
        if component_type == 'F':
            # voltage controlled current source
            
            nodeC = line[3]

            gain = sp.symbols(name)

            # if connected to ground
            if node1 == 0:
                B[index2, d_M[nodeC]] -= gain
                continue
            if node2 == 0:
                B[index1, d_M[nodeC]] += gain
                continue
            
            B[index1, d_M[nodeC]] += gain
            B[index2, d_M[nodeC]] -= gain

        if component_type == 'I':
            current = sp.symbols(name)
            # if connected to ground
            if node1 == 0:
                z[index2] += current
                continue
            if node2 == 0:
                z[index1] += -current
                continue
            z[index1] += -current
            z[index2] += current
    
        if component_type == 'O':
            nodeO = int(line[3])
            indexO = nodeO - 1
            B[indexO, M_] = 1
            if node1 == 0:
                C[M_, index2] = -1
                M_ += 1
                continue
            if node2 == 0:
                C[M_, index1] = 1
                M_ += 1
                continue
            B[indexO, M_] = 1
            C[M_, index1] = 1
            C[M_, index2] = -1
            M_ += 1
    # print(G)
    # print(B)
    # print(C)
    # print(D)


    A = sp.Matrix(sp.BlockMatrix([
        [G, B],
        [C, D]
    ]))
    
    print('The A matrix:')
    sp.pprint(A)
    print()

    v = sp.zeros(N, 1)
    for i in range(N):
        v[i] = sp.symbols('v_' + str(i+1))

    j = sp.zeros(M, 1)
    for i in range(M):
        j[i] = sp.symbols('I_' + l_M[i])

    x = sp.Matrix(sp.BlockMatrix([
        [v],
        [j]
    ]))

    print('The x matrix:')
    sp.pprint(x)
    print()

    print('The z matrix:')
    sp.pprint(z)
    print()

    print("The solution:")
    sp.pprint(sp.solve(A * x - z, x))
    print()

    print('Elapsed time is ', time.time() - start_time, 'seconds')



if __name__ == '__main__':
    scam(r'examples/exampleF.cir')