from operators import Operators


def load_initial_state(filename):
    result = {
        'cubes': [],
        'initial': [],
        'goal': []
    }
    f = open(filename, 'r').read()
    cubes_index = f.index('OBJECTS')
    initial_state_index = f.index('INITIAL-STATE')
    goals_index = f.index('GOALS')

    cubes_end_index = f[cubes_index:].index('\n')
    cubes_count = int(f[cubes_index + 8:cubes_end_index])
    cubes_names = [cube for cube in f[cubes_end_index + 1:initial_state_index].split('\n') if cube != '']

    initial_state_end_index = initial_state_index + f[initial_state_index:].index('\n')
    initial_state_predicates = [p for p in f[initial_state_end_index + 1:goals_index].split('\n') if p != '']

    goal_end_index = goals_index + f[goals_index:].index('\n')
    goal_state = [p for p in f[goal_end_index + 1:].split('\n') if p != '']

    for i in range(cubes_count):
        result['cubes'].append(cubes_names[i])

    for i in range(len(initial_state_predicates)):
        if initial_state_predicates[i] == 'ARM-EMPTY':
            result['initial'].append('ARM-EMPTY')
        elif initial_state_predicates[i] == 'CLEAR':
            result['initial'].append(f'CLEAR({initial_state_predicates[i+1]})')
        elif initial_state_predicates[i] == 'ON':
            result['initial'].append(f'ON({initial_state_predicates[i+1]},{initial_state_predicates[i+2]})')
        elif initial_state_predicates[i] == 'ON-TABLE':
            result['initial'].append(f'ON-TABLE({initial_state_predicates[i+1]})')

    for i in range(len(goal_state)):
        if goal_state[i] == 'ARM-EMPTY':
            result['goal'].append('ARM-EMPTY')
        elif goal_state[i] == 'CLEAR':
            result['goal'].append(f'CLEAR({goal_state[i + 1]})')
        elif goal_state[i] == 'ON':
            result['goal'].append(f'ON({goal_state[i + 1]},{goal_state[i + 2]})')
        elif goal_state[i] == 'ON-TABLE':
            result['goal'].append(f'ON-TABLE({goal_state[i + 1]})')

    return result
