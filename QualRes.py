from enum import Enum
class STATE(Enum):
    POSITIVE = '+'
    MAX = 100
    ZERO = 0
    INVALID = 'invalid'
CHANGE = {'increase', 'decrease', 'steady'}
UPDATE_COUNT = 1
class QuantityVolAndOut:
    current_state = STATE.ZERO
    def set_state(self, state):
        current_state = state
    def increase(self):
        if self.current_state == STATE.ZERO:
            self.current_state = STATE.POSITIVE
        elif self.current_state == STATE.POSITIVE:
            self.current_state = STATE.MAX
        elif self.current_state == STATE.MAX:
            self.current_state = STATE.INVALID
        update_dependencies(self, 'increase')
    def decrease(self):
        if self.current_state == STATE.ZERO:
            self.current_state = STATE.INVALID
        elif self.current_state == STATE.POSITIVE:
            self.current_state = STATE.ZERO
        elif self.current_state == STATE.MAX:
            self.current_state = STATE.POSITIVE
        update_dependencies(self, 'decrease')
    def steady(self):
        return

class QuantityInflow:
    current_state = STATE.ZERO
    def set_state(self, state):
        current_state = state
    def increase(self):
        if self.current_state == STATE.ZERO:
            self.current_state = STATE.POSITIVE
        update_dependencies(self, 'increase')
    def decrease(self):
        if self.current_state == STATE.POSITIVE:
            self.current_state = STATE.ZERO
        update_dependencies(self, 'decrease')
    def steady(self):
        return

tap = QuantityInflow()
sink = QuantityVolAndOut()
drain =QuantityVolAndOut()
QUANTITY = {tap, sink, drain}

def is_invalid_state():
    if (tap.current_state is STATE.INVALID) or (sink.current_state is STATE.INVALID) or (drain.current_state is STATE.INVALID):
        return True
    return False

def reset_states():
    tap.current_state = STATE.ZERO
    sink.current_state = STATE.ZERO
    drain.current_state = STATE.ZERO


def print_current_state():
    global UPDATE_COUNT
    print(UPDATE_COUNT, "TAP:", tap.current_state.value, "||","SINK:", sink.current_state.value,"||", "DRAIN",drain.current_state.value)
    UPDATE_COUNT += 1

def update_dependencies(quantity, change):
    # print_current_state()
    if is_invalid_state():
        return
    if quantity is tap and change == 'increase':
        sink.increase()
    elif quantity is drain and change == 'increase':
        sink.decrease()
    elif quantity is sink:
        method = getattr(drain, change)
        method()

idx = 1
for quantity in QUANTITY:
    reset_states()
    for state in STATE:
        if state is STATE.INVALID: continue
        quantity.set_state(state)
        for change in CHANGE:
            # while not is_invalid_state():
            method = getattr(quantity,change)
            method()
            idx += 1
            print_current_state()





