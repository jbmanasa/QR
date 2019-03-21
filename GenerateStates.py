from enum import Enum
from itertools import  product

QUANTITY = {'tap', 'sink', 'drain'}

INFLOW_VALUES = {'0','+'}
VOLUME_VALUES = {'0','+','MAX'}
OUTFLOW_VALUES = {'0', '+', 'MAX'}

CHANGE = {'0', '+', '-'}

INFLOW_STATES = product(INFLOW_VALUES, CHANGE)
VOLUME_STATES = product(VOLUME_VALUES, CHANGE)
OUTFLOW_STATES = product(OUTFLOW_VALUES,CHANGE)

SYSTEM_STATES = product(list(INFLOW_STATES), list(VOLUME_STATES), list(OUTFLOW_STATES))

for idx, sys_state in enumerate(list(SYSTEM_STATES)):
    print(idx, "Tap :" ,sys_state[0], "SINK : ", sys_state[1], "Drain : ", sys_state[2])
