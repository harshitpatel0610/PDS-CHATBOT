class SlotManager:

    @staticmethod
    def set_slot(state, slot, value):

        state.slots[slot] = value

    @staticmethod
    def get_slot(state, slot):

        return state.slots.get(slot)

    @staticmethod
    def has_slot(state, slot):

        return slot in state.slots

    @staticmethod
    def clear_slots(state):

        state.slots.clear()