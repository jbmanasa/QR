from enum import Enum
from itertools import  product
from graphviz import Digraph

TAP = 0
SINK = 1
DRAIN = 2
HEIGHT = 3
PRESSURE = 4

MAGNITUDE = 0
DERIVATIVE = 1

INFLOW_VALUES = ['0','+']
VOLUME_VALUES = ['0','+','MAX']
OUTFLOW_VALUES = ['0', '+', 'MAX']
PRESSURE_VALUES = ['0', '+', 'MAX']
HEIGHT_VALUES = ['0', '+', 'MAX']

CHANGE = ['0', '+', '-']

INFLOW_STATES = product(INFLOW_VALUES, CHANGE)
VOLUME_STATES = product(VOLUME_VALUES, CHANGE)
OUTFLOW_STATES = product(OUTFLOW_VALUES, CHANGE)
PRESSURE_STATES = product(PRESSURE_VALUES, CHANGE)
HEIGHT_STATES = product(HEIGHT_VALUES, CHANGE)

SYSTEM_STATES = product(list(INFLOW_STATES), list(VOLUME_STATES), list(OUTFLOW_STATES), list(HEIGHT_STATES), list(PRESSURE_STATES))

# for idx, sys_state in enumerate(list(SYSTEM_STATES)):
#     print(idx, "Tap :" ,sys_state[0], "SINK : ", sys_state[1], "Drain : ", sys_state[2])
AMBIG_STATES = []
def get_influence(mag, influence):
    result_change = ''
    if mag is '0' or influence is '0':
        result_change = '0'
    elif mag is '+':
        if influence is '+':
            result_change = '+'
        else:
            result_change = '-'
    elif mag is 'MAX':
        if influence is '+':
            result_change = '+'
        else:
            result_change = '-'
    else:
        print("Not handled!!") # TODO ?
    return result_change

def total_influence(i1, i2, isign1, isign2):
    if i1=='0': return i2
    if i2=='0': return i1
    if i1!=i2: # only possiblity is +,-
        # print("ambiguous", i1, i2, isign1, isign2)
        return 'ambigious' # alternatively can return 0 (assuming they work at the same rate)
    return i1 # they're the same

def is_valid_influence(tap, sink, drain, height, pressure):
    inflow_influence_on_volume = get_influence(tap[MAGNITUDE], '+')
    outflow_inlfuence_on_volume = get_influence(drain[MAGNITUDE],'-')

    final_inf = total_influence(inflow_influence_on_volume, outflow_inlfuence_on_volume,
                                tap[MAGNITUDE], drain[MAGNITUDE])

    if final_inf != sink[DERIVATIVE] and final_inf != 'ambigious':
        return False
    if final_inf == 'ambigious':
        AMBIG_STATES.append((tap,sink,drain, height, pressure))
    return True

def is_valid_vol_outflow_proportional(sink, drain):
    if sink[DERIVATIVE] == drain[DERIVATIVE]:
        return True
    return False

def is_valid__positive_proportional(quantity_1, quantity_2):
    if quantity_1[DERIVATIVE] == quantity_2[DERIVATIVE]:
        return True
    return False

def is_valid_max_volume_state(sink, drain):
    if drain[MAGNITUDE] is 'MAX' and sink[MAGNITUDE] is not 'MAX':
        return False
    if drain[MAGNITUDE] is not 'MAX' and sink[MAGNITUDE] is 'MAX':
        return False
    return True

def is_valid_pressure_outflow_state(pressure, drain):
    if pressure[MAGNITUDE] != drain[MAGNITUDE]:
        return False
    return True

def is_valid_zero_volume_state(sink, drain, height, pressure):
    # if drain[MAGNITUDE] is not '0' and sink[MAGNITUDE] is '0':
    #     return False
    if sink[MAGNITUDE] is '0' and (drain[MAGNITUDE] != '0' or height[MAGNITUDE] != '0' or pressure[MAGNITUDE] != '0'):
        return False
    if height[MAGNITUDE] is '0' and sink[MAGNITUDE] is not '0':
        return False
    if pressure[MAGNITUDE] is '0' and sink[MAGNITUDE] is not '0':
        return False
    if drain[MAGNITUDE] is '0' and sink[MAGNITUDE] is not '0':
        return False
    return True

# def is_valid_no_magnitude_but_decresing(tap, sink, drain):
#     if sink[MAGNITUDE] is '0' and sink[DERIVATIVE] is '-': return False
#     if tap[MAGNITUDE] is '0' and tap[DERIVATIVE] is  '-': return False
#     if drain[MAGNITUDE] is '0' and drain[DERIVATIVE] is '-': return False
#     return True

def is_valid_no_magnitude_but_decresing(quantity):
    if quantity[MAGNITUDE] is '0' and quantity[DERIVATIVE] is '-': return False
    return True
def is_valid_max_magnitude_but_increasing(quantity):
    if quantity[MAGNITUDE] is 'MAX' and quantity[DERIVATIVE] is '+': return False
    return True

def is_equal_magnitude_state(quantity_1, quantity_2):
    if quantity_1[MAGNITUDE] != quantity_2[MAGNITUDE]:
        return False
    return True

def is_valid_state(state):
    #With this call we have only 12 valid states xd

    if not is_valid_influence(state[TAP], state[SINK], state[DRAIN], state[HEIGHT], state[PRESSURE]): #Does the inputs to this still remain the same?
        return False
    # if not is_valid_max_volume_state(state[SINK], state[DRAIN]):
    #     return False
    if not is_valid_zero_volume_state(state[SINK], state[DRAIN], state[HEIGHT], state[PRESSURE]):
        return False
    for quantity in state:
        if not is_valid_no_magnitude_but_decresing(quantity):
            return False
        if not is_valid_max_magnitude_but_increasing(quantity):
            return False

    if not is_valid__positive_proportional(state[SINK], state[HEIGHT]):
        return False
    if not is_valid__positive_proportional(state[HEIGHT], state[PRESSURE]):
        return False
    if not is_valid__positive_proportional(state[PRESSURE], state[DRAIN]):
        return False
    if not is_valid_pressure_outflow_state(state[PRESSURE], state[DRAIN]):
        return False
    if not is_equal_magnitude_state(state[SINK], state[HEIGHT]): #Not sure if this is correct
        return False
    if not is_equal_magnitude_state(state[HEIGHT], state[PRESSURE]): #Not sure if this is correct
        return False
    if not is_equal_magnitude_state(state[PRESSURE], state[DRAIN]): #Not sure if this is correct
        return False
    return True


VALID_STATE_COUNT = 0
INVALID_STATE_COUNT = 0

valid_states = {}
for sys_state in list(SYSTEM_STATES):
    if not is_valid_state(sys_state):
        INVALID_STATE_COUNT += 1
        # print("----------- : ", "Tap :" ,sys_state[TAP], "SINK : ", sys_state[SINK], "Drain : ", sys_state[DRAIN])
    else:
        VALID_STATE_COUNT += 1
        valid_states[sys_state]=[]
        # print("Valid State : ", "Tap :", sys_state[TAP], "SINK : ", sys_state[SINK], "Drain : ", sys_state[DRAIN])

print("Number of Valid states = ", VALID_STATE_COUNT)
print("Number of Invalid states = ", INVALID_STATE_COUNT)

""" ----------------------------------------------------------
    Generate Transitions -------------------------------------
    ----------------------------------------------------------"""

def get_next_landmark(quantity, current_landmark, derivative):
    next_landmark = None
    idx = None
    if quantity is 'tap':
        VALUES = INFLOW_VALUES
    elif quantity is 'sink':
        VALUES = VOLUME_VALUES
    elif quantity is 'height':
        VALUES = HEIGHT_VALUES
    elif quantity is 'pressure':
        VALUES = PRESSURE_VALUES
    elif quantity is 'drain':
        VALUES = OUTFLOW_VALUES

    if derivative is '+':
        idx = VALUES.index(current_landmark)
        if idx == len(VALUES) - 1:
            next_landmark = current_landmark
        else:
            next_landmark = VALUES[idx+1]
    elif derivative is '-':
        idx = VALUES.index(current_landmark)
        if idx == 0:
            next_landmark = current_landmark
        else:
            next_landmark = VALUES[idx - 1]
    else:
        next_landmark = current_landmark
    # if current_landmark == 'MAX' and derivative is '0':
    #     print(next_landmark)
    return (next_landmark, derivative)

Graph_states = set()
def create_nodes_and_edge(state1, state2, graph):
    state1_name = str(state1).replace('MAX', 'max').replace('), (', '\n').replace('(', '').replace(')', '').replace(
        '\'', '')
    state2_name = str(state2).replace('MAX', 'max').replace('), (', '\n').replace('(', '').replace(')', '').replace(
        '\'', '')
    graph.node(state1_name, color='blue')
    graph.node(state2_name, color='blue')
    graph.edge(state1_name, state2_name)
    Graph_states.add(state1_name)
    Graph_states.add(state2_name)

def transitions(state, graph, all_states):
     tap, sink, drain, height, pressure = state[0], state[1], state[2], state[3], state[4]
     next_landmark_tap = get_next_landmark('tap', tap[MAGNITUDE], tap[DERIVATIVE])
     next_landmark_sink = get_next_landmark('sink', sink[MAGNITUDE], sink[DERIVATIVE])
     next_landmark_drain = get_next_landmark('drain', drain[MAGNITUDE], drain[DERIVATIVE])
     next_landmark_height = get_next_landmark('height', height[MAGNITUDE], height[DERIVATIVE])
     next_landmark_pressure = get_next_landmark('pressure', pressure[MAGNITUDE], pressure[DERIVATIVE])
     # print(next_landmark_tap, next_landmark_sink, next_landmark_height, next_landmark_pressure, next_landmark_drain)
     tap_ps = set(list(product(tap, next_landmark_tap)))
     sink_ps = set(list(product(sink, next_landmark_sink)))
     # print(sink_ps)
     drain_ps = set(list(product(drain, next_landmark_drain)))
     height_ps = set(list(product(height, next_landmark_height)))
     pressure_ps = set(list(product(pressure, next_landmark_pressure)))
     sys_state_ps = product(tap_ps, sink_ps, drain_ps, height_ps, pressure_ps)
     # print(list(sys_state_ps))
     # next_state = (next_landmark_tap, next_landmark_sink,next_landmark_drain, next_landmark_height, next_landmark_pressure)
     for next_state in list(sys_state_ps):
         if next_state == state:
             continue
         if next_state in valid_states:
            create_nodes_and_edge(state, next_state, graph)
            # transitions(next_state, graph, all_states)
         else:
             None
             # print("Invalid state from", state, "to", next_state)

def affecting_connections (q1, val1, model, state2s):
    for (ival, q2) in val1['I']:
        influencer_mag = '+' if model[q1]['next'][0] == 'MAX' else model[q1]['next'][0]
        if influencer_mag != '0':
            new_derivative = influencer_mag if ival == '+' else ('+' if influencer_mag == '-' else '-')
            if not (new_derivative == '+' and model[q2]['next'][0] == 'MAX'):
                model[q2]['next'] = (model[q2]['next'][0], new_derivative)
                state2s.add(get_next_assignment(model))

    for (pval, q2) in val1['P']:
        new_derivative = model[q1]['next'][1] if pval == '+' else ('+' if model[q1]['next'][1] == '-' else '-')
        model[q2]['next'] = (model[q2]['next'][0], new_derivative)
        state2s.add(get_next_assignment(model))

    for (cval, q2) in val1['V']:  # correspond magnitudes
        model[q2]['next'] = (model[q1]['next'][0], model[q2]['next'][1])
        state2s.add(get_next_assignment(model))

def get_name(state):
    # return str(state).replace('MAX', 'max').replace(
    #     '), (', '\n').replace('(', '').replace(')', '').replace('\'', '')
    node_name = ""
    names = ['I (', 'V (', 'O (', 'H (', 'P (']
    for i, quantity in enumerate(state):
        node_name += names[i] + str(quantity).replace('MAX', 'max').replace('(', '').replace(')', '').replace('\'', '') + ')'
        if i != len(state)-1: node_name+='\n'
    return node_name


def generate_transitions(state, graph, all_states, model, next_val):
    state1_name = get_name(state)
    graph.node(state1_name)
    tap, sink, drain, height, pressure = state
    print('now:', tap, sink, drain, height, pressure)
    model['inflow']['now'] = tap
    model['volume']['now'] = sink
    model['outflow']['now'] = drain
    model['height']['now'] = height
    model['pressure']['now'] = pressure

    state2s = set()
    for i, (q1, val1) in enumerate(model.items()):
        model['inflow']['next'] = tap
        model['volume']['next'] = sink
        model['outflow']['next'] = drain
        model['height']['next'] = height
        model['pressure']['next'] = pressure

        next_value = next_val[val1['now']]
        if next_value:
            model[q1]['next'] = next_value
            state2s.add(get_next_assignment(model))

        for j, (q1, val1) in enumerate(model.items()):
            affecting_connections(q1, val1, model, state2s)

        for j, (q1, val1) in enumerate(list(model.items())[::-1]):
            affecting_connections(q1, val1, model, state2s)

    for state2 in list(state2s)[:]: # connect edges
        if state2 in AMBIG_STATES:
            state2s.add((state2[0], (state2[1][0], '-'), (state2[2][0], '-'), (state2[3][0], '-'), (state2[4][0], '-')))
            state2s.add((state2[0], (state2[1][0], '0'), (state2[2][0], '0'), (state2[3][0], '0'), (state2[4][0], '0')))
            state2s.add((state2[0], (state2[1][0], '+'), (state2[2][0], '+'), (state2[3][0], '+'), (state2[4][0], '+')))

    for state2 in state2s: # connect edges
        if state2 in all_states:
            state2_name = get_name(state2)

            if state2 not in all_states[state] and state2 != state:
                graph.edge(state1_name, state2_name) # draw edge
                all_states[state].append(state2)     # save edge
        else:
            print("couldnt find:", str(state2))

def get_next_assignment(model):
    t = ()
    for key,val in model.items():
        t += (val['next'], )
    return t

def generate_transitions_inflow(state, graph, all_states, drawn, model, next_value):
    state1_name = get_name(state)
    graph.node(state1_name)
    tap, sink, drain, height, pressure = state
    print('now:', tap, sink, drain, height, pressure)
    model['inflow']['now'] = tap
    model['volume']['now'] = sink
    model['outflow']['now'] = drain
    model['height']['now'] = height
    model['pressure']['now'] = pressure

    state2s = set()
    q1 = 'inflow' # we are just interested in next state of inflow
    val1 = model['inflow']
    model['inflow']['next'] = tap
    model['volume']['next'] = sink
    model['outflow']['next'] = drain
    model['height']['next'] = height
    model['pressure']['next'] = pressure

    if next_value: #MAP TO NEXT STATE/BEHAVIOR
        model[q1]['next'] = next_value
        state2s.add(get_next_assignment(model))

    for j, (q1, val1) in enumerate(model.items()):
        affecting_connections(q1, val1, model, state2s) # value corres. proportion, influence

    for j, (q1, val1) in enumerate(list(model.items())[::-1]):
        affecting_connections(q1, val1, model, state2s)

    for state2 in list(state2s)[:]: # handle ambigious seperately in case not handled.
        if state2 in AMBIG_STATES:
            state2s.add((state2[0], (state2[1][0], '-'), (state2[2][0], '-'), (state2[3][0], '-'), (state2[4][0], '-')))
            state2s.add((state2[0], (state2[1][0], '0'), (state2[2][0], '0'), (state2[3][0], '0'), (state2[4][0], '0')))
            state2s.add((state2[0], (state2[1][0], '+'), (state2[2][0], '+'), (state2[3][0], '+'), (state2[4][0], '+')))

    for state2 in state2s: # connect edges
        if state2 in all_states:
            state2_name = get_name(state2)

            if (state,state2) not in drawn and state2 != state:
                print("found", state2)
                graph.node(state2_name)
                graph.edge(state1_name, state2_name, label='trace') # draw edge
                all_states[state].append(state2)     # save edge
                drawn.add((state,state2))
        else:
            print("couldnt find:", str(state2))

def graph_from_behavior(g1, inflow_behavior, valid_states):
    g1.node('start state', shape='Mdiamond')
    drawn = set()
    for state, connections in valid_states.items():
        if state[0] == inflow_behavior[0]:  # FIND START STATES
            state1_name = get_name(state)
            g1.node(state1_name)
            g1.edge('start state', state1_name, label='initial state')

            # for state2 in connections: # PUT IN CONNECTIONS OF START STATES (NOT NECESSARY ANYMORE)
            #     state2_name = get_name(state2)
            #     if (state, state2) not in drawn:
            #         g1.edge(state1_name, state2_name)
            #         drawn.add((state, state2))

            for i in range(len(inflow_behavior) - 1):  # MAP TO NEXT EXOGENOUS INFLOW STATE
                for state0, connections0 in valid_states.items():
                    if state0[0] == inflow_behavior[i]:
                        generate_transitions_inflow(state0, g1, valid_states, drawn, model, inflow_behavior[i + 1])

                for state0, connections0 in valid_states.items():  # PUT IN THE CONNECTIONS OF THE FINAL INFLOW STATE
                    if state0[0] == inflow_behavior[-1]:
                        state0_name = get_name(state0)

                        for state02 in connections0:  # connextions
                            if state0[0] == state02[0]:
                                state02_name = get_name(state02)

                                if (state0, state02) not in drawn and state0 != state02: #DRAW EDGE
                                    g1.node(state02_name)
                                    g1.edge(state0_name, state02_name, label='trace')
                                    drawn.add((state0, state02))

g = Digraph('G', filename='behavior_graph5.gv')
g.attr('edge', overlap='false')

print("Number of nodes in graph", len(Graph_states))

model = {'inflow': {'I': [('+', 'volume')],
                    'P': [],
                    'V': [],
                    'now': None, 'next': None},
         'volume': {'I': [],
                    'P': [('+', 'height')],
                    'V': [('MAX', 'outflow'), ('0', 'outflow'), ('+', 'outflow'),
                          ('MAX', 'pressure'), ('0', 'pressure'), ('+', 'pressure'),
                          ('MAX', 'height'), ('0', 'height'), ('+', 'height')],
                    'now': None, 'next': None},
         'outflow': {'I': [('-', 'volume')],
                     'P': [],
                     'V': [('MAX', 'volume'), ('0', 'volume'), ('+', 'volume'),
                          ('MAX', 'pressure'), ('0', 'pressure'), ('+', 'pressure'),
                          ('MAX', 'height'), ('0', 'height'), ('+', 'height')],
                     'now': None, 'next': None},
         'height': {'I': [],
                    'P': [('+', 'pressure')],
                    'V': [('MAX', 'volume'), ('0', 'volume'), ('+', 'volume'),
                          ('MAX', 'pressure'), ('0', 'pressure'), ('+', 'pressure'),
                          ('MAX', 'outflow'), ('0', 'outflow'), ('+', 'outflow')],
                    'now': None, 'next': None},
         'pressure': {'I': [],
                    'P': [('+', 'outflow')],
                    'V': [('MAX', 'volume'), ('0', 'volume'), ('+', 'volume'),
                          ('MAX', 'outflow'), ('0', 'outflow'), ('+', 'outflow'),
                          ('MAX', 'height'), ('0', 'height'), ('+', 'height')],
                    'now': None, 'next': None},
         }

next_val = {('0', '+'): ('+', '+'),
            ('+', '+'): ('MAX', '0'),
            ('+', '-'): ('0', '0'),
            ('0', '0'): None,
            ('+', '0'): None,
            ('MAX', '0'): None,
            ('MAX', '-'): ('+', '-')}

for state in valid_states.keys():
    generate_transitions(state, g, valid_states, model, next_val)
g.view()

g1 = Digraph('G', filename='parabolic_inflow5.gv')
g1.attr('edge', overlap='false')

inflow_behavior = [('0','+'),
                   ('+', '+'),
                   ('+', '0'),
                   ('+', '-'),
                   ('0', '0')]

graph_from_behavior(g1, inflow_behavior, valid_states)
g1.view()



