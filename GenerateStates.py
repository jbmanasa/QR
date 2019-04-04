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
        # print("ambiguous", i1, i2, isign1, isign2)
        return 'ambigious' # alternatively can return 0 (assuming they work at the same rate)
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

def generate_transitions(state, graph, all_states):
    state1_name = str(state).replace('MAX', 'max').replace('), (', '\n').replace('(', '').replace(')', '').replace('\'', '')
    # print(state1_name)
    graph.node(state1_name)
    if state1_name.count('0')==6:
        graph.node(state1_name, shape='doublecircle')
    tap, sink, drain = state[0], state[1], state[2]
    # print(tap, sink, drain)

    state2s = []
    if sink == ('MAX', '-'):
        state2s.append((tap, ('+', '-'), ('+', drain[1]))) # not max anymore, decreased
    elif sink == ('0', '+'):
        state2s.append((tap, ('+', '+'), ('+', drain[1]))) # not 0 anymore, increased
    elif sink == ('+', '-'):
        state2s.append((tap, ('0', '0'), ('0', '0'))) # TODO don't feel comfortable hardcoding x(
    elif sink == ('+', '+'):
        state2s.append((tap, ('+', 'MAX'), ('+', 'MAX'))) # Increased from + to max

    if tap == ('+', '-'): # goes to 0
        if drain == ('0', '0'):
            state2s.append((('0', '0'), (sink[0], '0'), drain))  #TODO not sure correct approach
        else:
            state2s.append((('0', '0'), sink, drain))

    elif drain == ('+', '-'): # goes to zero
            state2s.append((tap, ('0', '0'), ('0', '0')))

    if tap == ('0', '+'):
        graph.node(state1_name, color='blue')
        state2s.append((('+', '+'), ('+', sink[1]), ('+', drain[1])))  # not 0 anymore, increased
        state2s.append((('+', '-'), ('+', sink[1]), ('+', drain[1])))  # not 0 anymore, increased
        state2s.append((('+', '0'), ('+', sink[1]), ('+', drain[1])))  # not 0 anymore, increased

    if drain == ('0', '+'):
        graph.node(state1_name, color='blue')
        state2s.append((tap, ('+', sink[1]), ('+', sink[1])))

    for state2 in state2s: # connect edges
        if state2 in all_states:
            state2_name = str(state2).replace('MAX', 'max').replace('), (', '\n').replace('(', '').replace(')', '').replace('\'', '')
            if state2 not in all_states[state]:
                graph.edge(state1_name, state2_name) # draw edge
                all_states[state].append(state2)     # save edge
        else:
            print("couldnt find:", str(state2))


g = Digraph('G', filename='behavior_graph.gv', engine='sfdp')

for state in valid_states.keys():
    generate_transitions(state, g, valid_states)


# print(valid_states) # keys: valid states, values: connected (&directed) states/edges
# print(AMBIG_STATES)
g.view()
