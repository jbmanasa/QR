from enum import Enum
class STATE(Enum):
    POSITIVE = '+'
    MAX = 100
    ZERO = 0
    INVALID = True
CHANGE = {'increase', 'decrease', 'steady'}

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
    def decrease(self):
        if self.current_state == STATE.ZERO:
            self.current_state = STATE.INVALID
        elif self.current_state == STATE.POSITIVE:
            self.current_state = STATE.ZERO
        elif self.current_state == STATE.MAX:
            self.current_state = STATE.POSITIVE
    def steady(self):
        return

class QuantityInflow:
    current_state = STATE.ZERO
    def set_state(self, state):
        current_state = state
    def increase(self):
        if self.current_state == STATE.ZERO:
            self.current_state = STATE.POSITIVE
    def decrease(self):
        if self.current_state == STATE.POSITIVE:
            self.current_state = STATE.ZERO
    def steady(self):
        return

tap = QuantityInflow()
sink = QuantityVolAndOut()
drain =QuantityVolAndOut()
QUANTITY = {tap, sink, drain}
idx = 1
for quantity in QUANTITY:
    for state in STATE:
        for change in CHANGE:
            print(idx, "tap---",tap.current_state,"sink-----", sink.current_state,"drain-----", drain.current_state)
            quantity.set_state(state)
            method = getattr(quantity,change)
            method()
            idx += 1





