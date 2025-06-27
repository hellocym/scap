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

def scam(fname):
    # read the file
    f = open(fname, 'r')
    lines = f.readlines()
    
    N = 0   # number of nodes
    M = 0   # number of voltage sources
    l_M = []   # list of voltage sources

    # get the number of nodes and voltage sources
    for line in lines:
        # parse the line
        line = line.split()
        # get the type of the component
        component_type = line[0][0]
        if component_type in ['V', 'E', 'H']:
            M += 1
            l_M.append(line[0])
        node1, node2 = line[1], line[2]
        N = max(N, int(node1), int(node2))

    # initialize the matrices
    G = sp.zeros(N, N)   # conductance matrix
    B = sp.zeros(N, M)   # voltage source matrix 1
    C = sp.zeros(M, N)   # voltage source matrix 2
    D = sp.zeros(N, M)   # controlled source matrix
    s = sp.symbols('s')  # laplace variable

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
            if resistance == 'Symbolic':
                resistance = sp.symbols(name)
            else:
                resistance = float(resistance)
            
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
            if capacitance == 'Symbolic':
                capacitance = sp.symbols(name)
            else:
                capacitance = float(capacitance)

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
            if inductance == 'Symbolic':
                inductance = sp.symbols(name)
            else:
                inductance = float(inductance)
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
            voltage = line[3]

        if component_type == '':


if __name__ == '__main__':
    scam(r'examples/example0.cir')