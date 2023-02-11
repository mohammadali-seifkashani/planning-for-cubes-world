import numpy as np
from initial import load_initial_state
from operators import operators
from show_state import show_state
import itertools


def satisfies(s, g):
    for goal_atom in g:
        if goal_atom not in s:
            return False
    return True


def applicable_options(s, all_cubes):
    result = []

    for cube in all_cubes:
        pick_up_preconds = operators.pick_up_preconditions(s, cube)
        put_down_preconds = operators.put_down_preconditions(s, cube)
        if type(pick_up_preconds) == list:
            result.append((operators.pick_up, (s, cube), pick_up_preconds))
        if type(put_down_preconds) == list:
            result.append((operators.put_down, (s, cube), put_down_preconds))

        for cube2 in all_cubes:
            if cube2 == cube:
                continue
            stack_precons = operators.stack_preconditions(s, cube, cube2)
            unstack_preconds = operators.unstack_preconditions(s, cube, cube2)
            if type(stack_precons) == list:
                result.append((operators.stack, (s, cube, cube2), stack_precons))
            if type(unstack_preconds) == list:
                result.append((operators.unstack, (s, cube, cube2), unstack_preconds))

    return result


def renew_options(new_options, options):
    for no in new_options:
        if no not in options:
            options.append(no)


def create_all_p(s, all_cubes):
    s = tuple(s)
    result = {(s, 'ARM-EMPTY'): np.inf}
    for cube in all_cubes:
        result[(s, f'CLEAR({cube})')] = np.inf
        result[(s, f'HOLDING({cube})')] = np.inf
        result[(s, f'ON-TABLE({cube})')] = np.inf
        for cube2 in all_cubes:
            if cube2 == cube:
                continue
            result[(s, f'ON({cube},{cube2})')] = np.inf

    # for simplicity: first we put inf in all predicates (result[s, p] = np.inf).
    # then put 0 in predicates that were in state s previously
    # see first line of implementation of delta function in page 8 of slide
    for p in s:
        result[(s, p)] = 0

    return result


def initialize_delta_table(s, all_cubes):
    s = tuple(s)
    result = create_all_p(s, all_cubes)
    level_2_result = {}

    for k, v in result.items():
        for k1, v1 in result.items():
            temp_list = [k[1]]
            if k1[1] != k[1]:
                temp_list.append(k1[1])
                if (s, tuple(temp_list[::-1])) not in level_2_result:
                    if k[1] in s and k1[1] in s:
                        level_2_result[(s, tuple(temp_list))] = 0
                    else:
                        level_2_result[(s, tuple(temp_list))] = np.inf

    merged_result = {}
    for d in (result, level_2_result): merged_result.update(d)
    return merged_result


# implementation of delta0(s,p) due to 7th line of delta0 code.
def preconds_sum_delta0(actions_preconds, result, s):
    psd = 1
    s = tuple(s)
    for ap in actions_preconds:
        if np.isinf(result[(s, ap)]):
            psd = np.inf
            break
        psd += result[(s, ap)]
    return psd


def get_pair_preconds_delta(s, delta_table, preconds):
    s = tuple(s)
    k = (s, tuple(preconds))
    if k not in delta_table:
        k = (s, tuple(preconds[::-1]))
    return delta_table[k]


def get_delta_one_predicate(s, delta_table, preconds):
    s = tuple(s)
    if len(preconds) == 1:
        return delta_table[(s, preconds[0])] + 1
    if len(preconds) == 2:
        delta_value = get_pair_preconds_delta(s, delta_table, preconds)
        return delta_value + 1
    else:
        pair_conditions_delta_values = []
        pair_combinations_list = []
        for comb in itertools.combinations(preconds, 2):
            pair_combinations_list.append(list(comb))
            delta_value = get_pair_preconds_delta(s, delta_table, list(comb))
            pair_conditions_delta_values.append(delta_value)
        # if delta_table[(('ON_TABLE(a)', 'ON(c,a)', 'CLEAR(c)', 'HOLDING(b)'), 'HOLDING(a)')] == 3:
        #     print('preconds', preconds)
        #     print(pair_conditions_delta_values)
        #     exit()
        return max(pair_conditions_delta_values) + 1


def get_delta_two_predicates(s, delta_table, preconds, positive_effects):
    result = delta_table.copy()
    new_delta_table = {}
    for k, v in result.items():
        v1, v2, v3 = np.inf, np.inf, np.inf
        if type(k[1]) != str:
            if k[1][0] in positive_effects and k[1][1] in positive_effects:
                v1 = get_delta_one_predicate(s, delta_table, preconds)
            elif k[1][0] in positive_effects and k[1][1] not in positive_effects:
                new_preconds = list(set([k[1][1]] + preconds))
                v2 = get_delta_one_predicate(s, delta_table, new_preconds)
            elif k[1][0] not in positive_effects and k[1][1] in positive_effects:
                new_preconds = list(set([k[1][0]] + preconds))
                v3 = get_delta_one_predicate(s, delta_table, new_preconds)
            new_delta_table[k] = min(min(v1, v2, v3), result[k])
    for k, v in new_delta_table.items():
        result[k] = v
    return result


def update_delta_2(s, delta_table, U, all_cubes):
    result = delta_table.copy()
    options = applicable_options(U, all_cubes)
    # print('curren U is: ', U)
    # print('applicable options: ', [i[0] for i in options])
    for action_function, action_args, actions_preconds in options:
        positive_effects = action_function(*action_args, just_positive=True)
        before_len = len(U)
        U += positive_effects
        U = list(set(U))
        if len(U) == before_len:
            continue
        # print(action_function)
        # print('positive effects: ', positive_effects)
        for p in positive_effects:
            psd = get_delta_one_predicate(s, result, actions_preconds)
            result[(tuple(s), p)] = min(result[(tuple(s), p)], psd)

        result = get_delta_two_predicates(s, result, actions_preconds, positive_effects)

    return U, result


def update_delta(s, result, U, all_cubes):
    options = applicable_options(U, all_cubes)  # [(action_function, (action_inputs), action_preconds)]
    result_copy = result.copy()
    for action_function, action_args, actions_preconds in options:
        positive_effects = action_function(*action_args, just_positive=True)
        U += positive_effects
        U = list(set(U))

        # line 6th and 7th of delta0 code
        for p in positive_effects:
            psd = preconds_sum_delta0(actions_preconds, result_copy, s)
            result_copy[(tuple(s), p)] = min(result_copy[(tuple(s), p)], psd)

    return U, result_copy


def get_state_gaol_delta(s, g, result):
    dist_list = []
    for comb in itertools.combinations(g, 2):
        dist = get_pair_preconds_delta(s, result, list(comb))
        dist_list.append(dist)
    return max(dist_list)
    # dist = 0
    # for item in g:
    #     dist += result[(tuple(s), item)]
    # return dist


def delta_2(s, g, all_cubes):
    initial_data_table = initialize_delta_table(s, all_cubes)
    U = s.copy()
    counter = 1
    while True:
        new_U, new_result = update_delta_2(s, initial_data_table, U, all_cubes)
        # print(counter, 'rrrrrr', new_result)
        counter += 1
        if initial_data_table == new_result:
            # print('final result: ', new_result)
            # print('new U', new_U)
            goal_distance = get_state_gaol_delta(s, g, initial_data_table)
            return goal_distance
            # print('goal_distance', goal_distance)
            # exit()
            # break
        else:
            U = new_U
            initial_data_table = new_result



def delta(s, g, all_cubes):
    result = create_all_p(s, all_cubes)
    U = s.copy()
    while True:
        new_U, new_result = update_delta(s, result, U, all_cubes)
        if result == new_result:
            # print('final result: ', result)
            goal_distance = get_state_gaol_delta(s, g, result)
            break
        else:
            U = new_U
            result = new_result
    # print(goal_distance)
    return goal_distance


def heuristic_forward_search(pi, s, g, all_cubes):
    print('state', s)
    if satisfies(s, g):
        return pi

    # options = actions
    options = applicable_options(s, all_cubes)
    print('options: ', options)
    # list of delta0(lambda(s,a), g) for different actions a
    delta_with_g = []

    # list of lambda(s, a) for different actions a
    lambdas = []
    actions = []
    # 3rd line of HFS function (for delta0)
    # TODO implementation is based on delta0. We need implementation for delta2!
    for action_function, action_args, actions_preconds in options:
        effects, action = action_function(*action_args, just_positive=False)
        # print('action function is: ', action, 'action effects: ', effects)
        # delta_out = delta(effects, g, all_cubes)
        delta_out = delta_2(effects, g, all_cubes)
        lambdas.append(effects)
        actions.append(action)
        delta_with_g.append(delta_out)
    # print('actions', actions)
    # print('delta', delta_with_g)

    # "while" part of HFS function
    while options:
        # 5th and 6th line of HFS function
        selected_action_index = np.argmin(delta_with_g)
        options.pop(selected_action_index)
        new_a = actions[selected_action_index]

        # 7th line of HFS function
        pi_prime = heuristic_forward_search(pi + [new_a], lambdas[selected_action_index], g, all_cubes)

        # 8th line of HFS function
        if pi_prime is not False:
            return pi_prime

    # last line of HFS function
    return False


def main():
    pi = []
    s0 = load_initial_state('blocks-world (simplified)/reversal4.txt')
    print(s0)
    show_state(s0['initial'])
    show_state(s0['goal'])
    pi = heuristic_forward_search(pi, s0['initial'], s0['goal'], s0['cubes'])
    print(pi)


main()
