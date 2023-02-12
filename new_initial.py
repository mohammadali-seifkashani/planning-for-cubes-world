def load_initial_state(filename):
    result = {
        'objects': [],
        'initial': [],
        'goal': []
    }
    f = open(filename, 'r').read()
    objects_index = f.index('OBJECTS')
    initial_state_index = f.index('INITIAL-STATE')
    goals_index = f.index('GOALS')

    objects_end_index = f[objects_index:].index('\n')
    objects_count = int(f[objects_index + 8:objects_end_index])
    objects_names = [cube for cube in f[objects_end_index + 1:initial_state_index].split('\n') if cube != '']

    initial_state_end_index = initial_state_index + f[initial_state_index:].index('\n')
    initial_state_predicates = [p for p in f[initial_state_end_index + 1:goals_index].split('\n') if p != '']

    goal_end_index = goals_index + f[goals_index:].index('\n')
    goal_state = [p for p in f[goal_end_index + 1:].split('\n') if p != '']

    for i in range(objects_count):
        result['objects'].append(objects_names[i])

    for i in range(len(initial_state_predicates)):
        if initial_state_predicates[i] == 'HAVE-GRIPPER':
            result['initial'].append(f'HAVE-GRIPPER({initial_state_predicates[i+1]},{initial_state_predicates[i+2]})')
        elif initial_state_predicates[i] == 'AT-ROOM':
            result['initial'].append(f'AT-ROOM({initial_state_predicates[i+1]},{initial_state_predicates[i+2]})')
        elif initial_state_predicates[i] == 'HOLDING':
            result['initial'].append(f'HOLDING({initial_state_predicates[i+1]},{initial_state_predicates[i+2]})')
        elif initial_state_predicates[i] == 'EMPTY':
            result['initial'].append(f'EMPTY({initial_state_predicates[i+1]})')

    for i in range(len(goal_state)):
        if goal_state[i] == 'HAVE-GRIPPER':
            result['goal'].append(f'HAVE-GRIPPER({goal_state[i+1]},{goal_state[i+2]})')
        elif goal_state[i] == 'AT-ROOM':
            result['goal'].append(f'AT-ROOM({goal_state[i+1]},{goal_state[i+2]})')
        elif goal_state[i] == 'HOLDING':
            result['goal'].append(f'HOLDING({goal_state[i+1]},{goal_state[i+2]})')
        elif goal_state[i] == 'EMPTY':
            result['goal'].append(f'EMPTY({initial_state_predicates[i+1]})')

    return result


