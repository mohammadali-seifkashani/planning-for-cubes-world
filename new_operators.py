class Operators:
    def __init__(self):
        pass

    def go(self, s: list, rob: str, room1: str, room2: str, just_positive=False):
        s = s.copy()
        # preconditions
        check = self.go_preconditions(s, rob, room1, room2)
        if type(check) == str:
            raise Exception(check)
        positive_effects = list()
        positive_effects.append(f'AT-ROOM({rob},{room1})')
        if just_positive:
            return positive_effects
        at_room1 = s.index(f'AT-ROOM({rob},{room1})')
        s.extend(positive_effects)
        s.pop(at_room1)
        return s, f'AT-ROOM {rob} {room1}'

    @staticmethod
    def go_preconditions(s: list, rob: str, room1: str, room2: str):
        temp_s = s.copy()
        if f'AT-ROOM({rob},{room1})' not in temp_s:
            return f'not AT-ROOM({rob},{room1}) in room'
        return [f'AT-ROOM({rob},{room1})']

    def put_down(self, s: list, rob: str, grp: str, ball: str, room1: str, just_positive=False):
        s = s.copy()
        # preconditions
        check = self.put_down_preconditions(s, rob, grp, ball, room1)
        if type(check) == str:
            raise Exception(check)

        positive_effects = list()
        positive_effects.append(f'AT-ROOM({ball},{room1})')
        positive_effects.append(f'EMPTY({grp})')
        if just_positive:
            return positive_effects
        s.extend(positive_effects)
        holding_ball = s.index(f'HOLDING({grp},{ball})')
        s.pop(holding_ball)
        return s, f'PUT-DOWN {rob} {grp} {ball} {room1}'

    @staticmethod
    def put_down_preconditions(s: list, rob: str, grp: str, ball: str, room1: str):
        temp_s = s.copy
        if f'AT-ROOM({rob},{room1})' not in temp_s:
            return f'not AT-ROOM({rob},{room1}) in room'
        if f'HOLDING({grp}, {ball})' not in temp_s:
            return f'not HOLDING({grp}, {ball})'
        if f'HAVE-GRIPPER({rob},{grp})' not in temp_s:
            return f'not GRIPPER({rob}, {grp})'
        return [f'AT-ROOM({rob},{room1})', f'HOLDING({grp}, {ball})', f'HAVE-GRIPPER({rob},{grp})']

    def pick_up(self, s: list, rob: str, grp: str, ball: str, room1: str, just_positive=False):
        s = s.copy()
        # preconditions
        check = self.pick_up_preconditions(s, rob, grp, ball, room1)
        if type(check) == str:
            raise Exception(check)

        positive_effects = list()
        positive_effects.append(f'HOLDING({grp}, {ball})')
        if just_positive:
            return positive_effects
        s.extend(positive_effects)
        at_room = s.index(f'AT-ROOM({rob},{room1})')
        s.pop(at_room)
        is_empty = s.index(f'EMPTY({grp})')
        s.pop(is_empty)
        return s, f'PICK-UP {rob} {grp} {ball} {room1}'

    @staticmethod
    def pick_up_preconditions(s: list, rob: str, grp: str, ball: str, room1: str):
        temp_s = s.copy()
        if f'AT-ROOM({rob},{room1})' not in temp_s:
            return f'not AT-ROOM({rob},{room1}) in room'
        if f'AT-ROOM({ball},{room1})' not in temp_s:
            return f'not AT-ROOM({ball},{room1}) in room'
        if f'HAVE-GRIPPER({rob},{grp})' not in temp_s:
            return f'not GRIPPER({rob}, {grp})'
        if f'EMPTY({grp})' not in temp_s:
            return f'not EMPTY({grp})'
        return [f'AT-ROOM({rob},{room1})', f'AT-ROOM({ball},{room1})', f'HAVE-GRIPPER({rob},{grp})', f'EMPTY({grp})']


operators = Operators()
