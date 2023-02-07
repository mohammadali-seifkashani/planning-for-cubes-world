class Operators:
    def __init__(self):
        pass

    def pick_up(self, s: list, ob1: str, just_positive=False):
        s = s.copy()
        # preconditions
        check = self.pick_up_preconditions(s, ob1)
        if type(check) == str:
            raise Exception(check)

        # effects
        s.append(f'HOLDING({ob1})')
        if just_positive:
            return [f'HOLDING({ob1})']
        ob1_clear_index = s.index(f'CLEAR({ob1})')
        s.pop(ob1_clear_index)
        ob1_ontable_index = s.index(f'ON_TABLE({ob1})')
        s.pop(ob1_ontable_index)
        arm_empty_index = s.index('ARM-EMPTY')
        s.pop(arm_empty_index)
        return s, f'PICK-UP({ob1})'

    @staticmethod
    def pick_up_preconditions(s: list, ob1: str):
        if f'CLEAR({ob1})' not in s:
            return 'Object must be clear!'
        if f'ON_TABLE({ob1})' not in s:
            return 'Object must be on table!'
        if 'ARM-EMPTY' not in s:
            return 'Arm must be empty!'
        return [f'CLEAR({ob1})', f'ON_TABLE({ob1})', 'ARM-EMPTY']

    def put_down(self, s: list, ob1: str, just_positive=False):
        s = s.copy()
        # preconditions
        check = self.put_down_preconditions(s, ob1)
        if type(check) == str:
            raise Exception(check)

        # effects
        positive_effects = list()
        positive_effects.append(f'CLEAR({ob1})')
        positive_effects.append(f'ON_TABLE({ob1})')
        positive_effects.append('ARM-EMPTY')
        if just_positive:
            return positive_effects
        s.extend(positive_effects)
        ob1_holding_index = s.index(f'HOLDING({ob1})')
        s.pop(ob1_holding_index)
        return s, f'PUT-DOWN({ob1})'

    @staticmethod
    def put_down_preconditions(s: list, ob1: str):
        if f'HOLDING({ob1})' not in s:
            return 'Object must be holding!'
        if 'ARM-EMPTY' in s:
            return 'Arm must not be empty!'
        return [f'HOLDING({ob1})']  # TODO adding ~ARM_EMPTY

    def stack(self, s: list, sob: str, sunderob: str, just_positive=False):
        s = s.copy()
        # preconditions
        check = self.stack_preconditions(s, sob, sunderob)
        if type(check) == str:
            raise Exception(check)

        # effects
        positive_effects = list()
        positive_effects.append(f'CLEAR({sob})')
        positive_effects.append('ARM-EMPTY')
        positive_effects.append(f'ON({sob},{sunderob})')
        if just_positive:
            return positive_effects
        s.extend(positive_effects)
        sob_holding_index = s.index(f'HOLDING({sob})')
        s.pop(sob_holding_index)
        sunderob_clear_index = s.index(f'CLEAR({sunderob})')
        s.pop(sunderob_clear_index)
        return s, f'STACK({sob},{sunderob})'

    @staticmethod
    def stack_preconditions(s: list, sob: str, sunderob: str):
        if sob == sunderob:
            return 'Equal objects passed!'
        if f'HOLDING({sob})' not in s:
            return 'First object must be holding!'
        # if 'ARM-EMPTY' in s:
        #     return 'Arm must not be empty!'
        if f'CLEAR({sunderob})' not in s:
            return 'Second object must be clear!'
        return [f'HOLDING({sob})', f'CLEAR({sunderob})']  # TODO adding ~ARM_EMPTY

    def unstack(self, s: list, sob: str, sunderob: str, just_positive=False):
        s = s.copy()
        # preconditions
        check = self.unstack_preconditions(s, sob, sunderob)
        if type(check) == str:
            raise Exception(check)

        # effects
        positive_effects = list()
        positive_effects.append(f'HOLDING({sob})')
        positive_effects.append(f'CLEAR({sunderob})')
        if just_positive:
            return positive_effects
        s.extend(positive_effects)
        sob_clear_index = s.index(f'CLEAR({sob})')
        s.pop(sob_clear_index)
        arm_empty_index = s.index(f'ARM-EMPTY')
        s.pop(arm_empty_index)
        on_sob_sunderob_index = s.index(f'ON({sob},{sunderob})')
        s.pop(on_sob_sunderob_index)
        return s, f'UNSTACK({sob},{sunderob})'

    @staticmethod
    def unstack_preconditions(s: list, sob: str, sunderob: str):
        if sob == sunderob:
            return 'Equal objects passed!'
        if f'ON({sob},{sunderob})' not in s:
            return 'First object must be on second one (sob.down != sunderob)!'
        if f'CLEAR({sob})' not in s:
            return 'First object must be clear!'
        if 'ARM-EMPTY' not in s:
            return 'Arm must be empty!'
        return [f'ON({sob},{sunderob})', f'CLEAR({sob})', 'ARM-EMPTY']


operators = Operators()
