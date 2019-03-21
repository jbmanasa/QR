from enum import Enum
from itertools import  product

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
OUTFLOW_STATES = product(OUTFLOW_VALUES,CHANGE)

SYSTEM_STATES = product(list(INFLOW_STATES), list(VOLUME_STATES), list(OUTFLOW_STATES))

# for idx, sys_state in enumerate(list(SYSTEM_STATES)):
#     print(idx, "Tap :" ,sys_state[0], "SINK : ", sys_state[1], "Drain : ", sys_state[2])

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
        print("Not handled!!")
    return result_change



def is_valid_influence(tap, sink, drain):
    inflow_influence_on_volume = get_influence(tap[MAGNITUDE], '+')
    outflow_inlfuence_on_volume = get_influence(drain[MAGNITUDE],'-')
    # print(inflow_influence_on_volume, outflow_inlfuence_on_volume)
    if inflow_influence_on_volume != outflow_inlfuence_on_volume:
        return False
    if tap[MAGNITUDE] is '+':
        print("Influence", inflow_influence_on_volume)
        print(drain[MAGNITUDE], sink[DERIVATIVE])
    if inflow_influence_on_volume != sink[DERIVATIVE]:
        return False
    return True

def is_valid_vol_outflow_proportional(sink, drain):
    return True

def is_valid_max_volume_state(sink, drain):
    if sink[MAGNITUDE] is 'MAX' and drain[MAGNITUDE] is not 'MAX':
        return False
    return True

def is_valid_zero_volume_state(sink, drain):
    if sink[MAGNITUDE] is '0' and drain[DERIVATIVE] is not '0':
        return False
    return True

def is_valid_state(state):
    #With this call we have only 12 valid states xd
    # if not is_valid_influence(state[TAP], state[SINK], state[DRAIN]):
    #     return False
    #Havent written this yet . Returns true for now
    if not is_valid_vol_outflow_proportional(state[SINK], state[DRAIN]):
        return False
    if not is_valid_max_volume_state(state[SINK], state[DRAIN]):
        return False
    if not is_valid_zero_volume_state(state[SINK], state[DRAIN]):
        return False
    return True

VALID_STATE_COUNT = 0
INVALID_STATE_COUNT = 0
for sys_state in list(SYSTEM_STATES):
    if not is_valid_state(sys_state):
        INVALID_STATE_COUNT += 1
        # print("Invalid State : ", "Tap :" ,sys_state[TAP], "SINK : ", sys_state[SINK], "Drain : ", sys_state[DRAIN])
    else:
        VALID_STATE_COUNT += 1
        print("Valid State : ", "Tap :", sys_state[TAP], "SINK : ", sys_state[SINK], "Drain : ", sys_state[DRAIN])

print("Number of Valid states = ", VALID_STATE_COUNT)
print("Number of Invalid states = ", INVALID_STATE_COUNT)