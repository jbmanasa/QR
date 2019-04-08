from enum import Enum
from itertools import  product
from graphviz import Digraph

TAP = 0
SINK = 1
DRAIN = 2

MAGNITUDE = 0
DERIVATIVE = 1

INFLOW_VALUES = {'0','+'}
VOLUME_VALUES = {'0','+','MAX'}
OUTFLOW_VALUES = {'0', '+', 'MAX'}

CHANGE = {'0', '+', '-'}

INFLOW_STATES = product(INFLOW_VALUES, CHANGE)
VOLUME_STATES = product(VOLUME_VALUES, CHANGE)
OUTFLOW_STATES = product(OUTFLOW_VALUES, CHANGE)

SYSTEM_STATES = product(list(INFLOW_STATES), list(VOLUME_STATES), list(OUTFLOW_STATES))

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
        return 'ambigious'
    return i1 # they're the same

def is_valid_influence(tap, sink, drain):
    inflow_influence_on_volume = get_influence(tap[MAGNITUDE], '+')
    outflow_inlfuence_on_volume = get_influence(drain[MAGNITUDE],'-')
    final_inf = total_influence(inflow_influence_on_volume, outflow_inlfuence_on_volume,
                                tap[MAGNITUDE], drain[MAGNITUDE])
    if final_inf != sink[DERIVATIVE] and final_inf != 'ambigious':
        return False
    if final_inf == 'ambigious':
        AMBIG_STATES.append((tap,sink,drain))
    return True

def is_valid_vol_outflow_proportional(sink, drain):
    if sink[DERIVATIVE] is '-' and drain[DERIVATIVE] is '-' :
        return True
    elif sink[DERIVATIVE] is '+' and drain[DERIVATIVE] is '+' :
        return True
    elif sink[DERIVATIVE] is '0' and drain[DERIVATIVE] is '0' :
        return True
    return False

def is_valid_max_volume_state(sink, drain):
    if drain[MAGNITUDE] is 'MAX' and sink[MAGNITUDE] is not 'MAX':
        return False
    if drain[MAGNITUDE] is not 'MAX' and sink[MAGNITUDE] is 'MAX':
        return False
    return True

def is_valid_zero_volume_state(sink, drain):
    if drain[MAGNITUDE] is '0' and sink[MAGNITUDE] is not '0':
        return False
    if drain[MAGNITUDE] is not '0' and sink[MAGNITUDE] is '0':
        return False
    return True

def is_valid_no_magnitude_but_decresing(tap, sink, drain):
    if sink[MAGNITUDE] is '0' and sink[DERIVATIVE] is '-': return False
    if tap[MAGNITUDE] is '0' and tap[DERIVATIVE] is  '-': return False
    if drain[MAGNITUDE] is '0' and drain[DERIVATIVE] is '-': return False

    if sink[MAGNITUDE] is 'MAX' and sink[DERIVATIVE] is '+': return False
    if drain[MAGNITUDE] is 'MAX' and drain[DERIVATIVE] is '+': return False
    return True

def is_valid_state(state):
    #With this call we have only 12 valid states xd
    if not is_valid_influence(state[TAP], state[SINK], state[DRAIN]):
        return False
    # TODO Havent written this yet. Returns true for now
    if not is_valid_vol_outflow_proportional(state[SINK], state[DRAIN]):
        return False
    if not is_valid_max_volume_state(state[SINK], state[DRAIN]):
        return False
    if not is_valid_zero_volume_state(state[SINK], state[DRAIN]):
        return False
    if not is_valid_no_magnitude_but_decresing(state[TAP], state[SINK], state[DRAIN]):
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

def get_name(state):
    node_name = ""
    names = ['I (', 'V (', 'O (', 'H (', 'P (']
    for i, quantity in enumerate(state):
        node_name += names[i] + str(quantity).replace('MAX', 'max').replace('(', '').replace(')', '').replace('\'', '') + ')'
        if i != len(state)-1: node_name+='\n'
    return node_name

def affecting_connections (q1, val1, model, state2s):
    print('ac', get_next_assignment(model))
    for (ival, q2) in val1['I']:
        influencer_mag = '+' if model[q1]['next'][0] == 'MAX' else model[q1]['next'][0]
        if influencer_mag != '0':
            new_derivative = influencer_mag if ival == '+' else ('+' if influencer_mag == '-' else '-')
            if not (new_derivative == '+' and model[q2]['next'][0] == 'MAX'):
                model[q2]['next'] = (model[q2]['next'][0], new_derivative)
                print('i', (model['inflow']['next'], model['volume']['next'], model['outflow']['next']))
                state2s.add((model['inflow']['next'], model['volume']['next'], model['outflow']['next']))

    for (pval, q2) in val1['P']:
        new_derivative = model[q1]['next'][1] if pval == '+' else ('+' if model[q1]['next'][1] == '-' else '-')
        model[q2]['next'] = (model[q2]['next'][0], new_derivative)
        print('p', (model['inflow']['next'], model['volume']['next'], model['outflow']['next']))
        state2s.add((model['inflow']['next'], model['volume']['next'], model['outflow']['next']))

    for (cval, q2) in val1['V']:  # correspond magnitudes
        model[q2]['next'] = (model[q1]['next'][0], model[q2]['next'][1])
        print('v', (model['inflow']['next'], model['volume']['next'], model['outflow']['next']))
        state2s.add((model['inflow']['next'], model['volume']['next'], model['outflow']['next']))

def generate_transitions(state, graph, all_states, model, next_val):
    state1_name = get_name(state)
    # print(state1_name)
    graph.node(state1_name)
    tap, sink, drain = state[0], state[1], state[2]
    print('now:', tap, sink, drain)
    model['inflow']['now'] = tap
    model['volume']['now'] = sink
    model['outflow']['now'] = drain

    state2s = set()
    for i, (q1, val1) in enumerate(model.items()):
        model['inflow']['next'] = tap
        model['volume']['next'] = sink
        model['outflow']['next'] = drain

        next_value = next_val[val1['now']]
        if next_value:
            model[q1]['next'] = next_value
            state2s.add((model['inflow']['next'], model['volume']['next'], model['outflow']['next']))

        for j, (q1, val1) in enumerate(model.items()):
            affecting_connections(q1, val1, model, state2s)

        for j, (q1, val1) in enumerate(list(model.items())[::-1]):
            affecting_connections(q1, val1, model, state2s)

    for state2 in list(state2s)[:]: # connect edges
        if state2 in AMBIG_STATES:
            state2s.add((state2[0], (state2[1][0], '-'), (state2[2][0], '-')))
            state2s.add((state2[0], (state2[1][0], '0'), (state2[2][0], '0')))
            state2s.add((state2[0], (state2[1][0], '+'), (state2[2][0], '+')))

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
    tap, sink, drain = state[0], state[1], state[2]
    print('now:', tap, sink, drain)
    model['inflow']['now'] = tap
    model['volume']['now'] = sink
    model['outflow']['now'] = drain

    state2s = set()
    q1 = 'inflow' # we are just interested in next state of inflow
    val1 = model['inflow']
    model['inflow']['next'] = tap
    model['volume']['next'] = sink
    model['outflow']['next'] = drain

    if next_value: #MAP TO NEXT STATE/BEHAVIOR
        model[q1]['next'] = next_value
        state2s.add(get_next_assignment(model))

    print('not reverse')
    for j, (q1, val1) in enumerate(model.items()):
        affecting_connections(q1, val1, model, state2s) # value corres. proportion, influence

    for j, (q1, val1) in enumerate(list(model.items())[::-1]):
        print('reverse')
        affecting_connections(q1, val1, model, state2s)

    for state2 in list(state2s)[:]: # handle ambigious seperately in case not handled.
        if state2 in AMBIG_STATES:
            state2s.add((state2[0], (state2[1][0], '-'), (state2[2][0], '-')))
            state2s.add((state2[0], (state2[1][0], '0'), (state2[2][0], '0')))
            state2s.add((state2[0], (state2[1][0], '+'), (state2[2][0], '+')))

    for state2 in state2s: # connect edges
        if state2 in all_states:
            state2_name = get_name(state2)

            if (state,state2) not in drawn and state2 != state:
                print("found", state2)
                graph.node(state2_name)
                graph.edge(state1_name, state2_name, label=get_trace(state, state2)) # draw edge
                all_states[state].append(state2)     # save edge
                drawn.add((state,state2))
        else:
            print("couldnt find:", str(state2))


def get_trace(state1, state2):
    if state1[0] != state2[0]:
        inflow = state2[0]
        if inflow == ('+,+'): return 'opening tap more'
        elif inflow == ('+', '0'): return 'stabilizing tap'
        elif inflow == ('+', '-'): return 'closing tap'
        elif inflow == ('0', '0'): return 'closed tap'
        elif inflow == ('0', '+'): return 'opened tap'



def graph_from_behavior(g1, inflow_behavior, valid_states):
    g1.node('start state', shape='Mdiamond')
    drawn = set()
    for state, connections in valid_states.items():
        if state[0] == inflow_behavior[0]:  # FIND START STATES
            state1_name = get_name(state)
            g1.node(state1_name)
            g1.edge('start state', state1_name, label='initial state')

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
                                    g1.edge(state0_name, state02_name, label=get_trace(state0, state02))
                                    drawn.add((state0, state02))



g = Digraph('G', filename='behavior_graph.gv')
g.attr('edge', overlap='false')

model = {'inflow': {'I': [('+', 'volume')],
                    'P': [],
                    'V': [],
                    'now': None, 'next': None},
         'volume': {'I': [],
                    'P': [('+', 'outflow')],
                    'V': [('MAX', 'outflow'), ('0', 'outflow'), ('+', 'outflow')],
                    'now': None, 'next': None},
         'outflow': {'I': [('-', 'volume')],
                     'P': [],
                     'V': [('MAX', 'volume'), ('0', 'volume'), ('+', 'outflow')],
                     'now': None, 'next': None}
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

g1 = Digraph('G', filename='parabolic_inflow.gv')
g1.attr('edge', overlap='false')

inflow_behavior = [('0','+'),
                   ('+', '+'),
                   ('+', '0'),
                   ('+', '-'),
                   ('0', '0')]

graph_from_behavior(g1, inflow_behavior, valid_states)
g1.view()

g2 = Digraph('G', filename='increasing_inflow.gv')
g2.attr('edge', overlap='false')

inflow_behavior = [('0','+'),
                   ('+', '+')]

graph_from_behavior(g2, inflow_behavior, valid_states)
g2.view()

# g3 = Digraph('G', filename='sinusoidal_inflow.gv')
# g3.attr('edge', overlap='false')
#
# inflow_behavior = [('0','+'),
#                    ('+', '+'),
#                    ('+', '0'),
#                    ('+', '-'),
#                    ('0', '0'),
#                    ('0', '+'),
#                    ('+', '+'),
#                    ('+', '0'),
#                    ('+', '-'),
#                    ('0', '0')]
#
# graph_from_behavior(g3, inflow_behavior, valid_states)
# g3.view()