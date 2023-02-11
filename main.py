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
    for action_function, action_args, actions_preconds in options:
        # print(action_function)
        positive_effects = action_function(*action_args, just_positive=True)
        # print('positive effects: ', positive_effects)
        U += positive_effects
        U = list(set(U))
        for p in positive_effects:
            psd = get_delta_one_predicate(s, result, actions_preconds)
            result[(tuple(s), p)] = min(result[(tuple(s), p)], psd)

        result = get_delta_two_predicates(s, result, actions_preconds, positive_effects)

    return U, result


def update_delta(s, result, U, all_cubes):
    options = applicable_options(U, all_cubes)  # [(action_function, (action_inputs), action_preconds)]
    result_copy = result.copy()
    # print('current state is: ', s)
    # print('state options :', options)
    # print('before U is: ', U)
    for action_function, action_args, actions_preconds in options:
        # TODO functionality for "just_positives" argument isn't implemented yet :)
        # if True, it should return just positive effects of an action
        positive_effects = action_function(*action_args, just_positive=True)
        # print('update delta action function: ', action_function, 'positive effects are: ', positive_effects)
        # in each iteration U will change. 5th line of delta0 code.
        U += positive_effects
        U = list(set(U))
        # when U changes, more actions (action = option) are applicable next iteration of U. See 4th line of delta0
        # code. "renew_options" function for this objective.

        # new_options = applicable_options(U, all_cubes)
        # renew_options(new_options, options)

        # line 6th and 7th of delta0 code
        for p in positive_effects:
            # print('ppppp', p)

            # this is why we needed "actions_preconds" as the 3rd value of tuples of "applicable_options" function.
            psd = preconds_sum_delta0(actions_preconds, result_copy, s)
            result_copy[(tuple(s), p)] = min(result_copy[(tuple(s), p)], psd)
            # print(f'delta value for {(tuple(s), p)} is: ', result[(tuple(s), p)])

        # print('first update results: ', result_copy)

    # print('after U is: ', U)
    return U, result_copy


def get_state_gaol_delta(s, g, result):
    dist = 0
    for item in g:
        dist += result[(tuple(s), item)]
    return dist


def delta_2(s, g, all_cubes):
    # TODO
    initial_data_table = initialize_delta_table(s, all_cubes)
    U = s.copy()
    counter = 1
    while True:
        new_U, new_result = update_delta_2(s, initial_data_table, U, all_cubes)
        if initial_data_table == new_result:
            print('final result: ', new_result)
            exit()
            goal_distance = get_state_gaol_delta(s, g, result)
            break
        else:
            U = new_U
            initial_data_table = new_result
    pass


def delta(s, g, all_cubes):
    # see first line of implementation of delta function in page 8 of slide
    # creating all predicates (all p) of delta0 list named "result"
    # TODO maybe we need to add all (p,q) pairs for delta2 too
    result = create_all_p(s, all_cubes)
    # print('result', result)
    # print('delta result: ', result)
    # U as the same as implementation of 8th page of slide
    # U will change but s shouldn't change always
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
    return result
    # options = actions

        # end of delta0 implementation

        # start of delta2 implementation
        # for p in positive_effects:
        #     for q in positive_effects:
        #         if p == q:
        #             continue
        #         min1 = result[(s, p)]
        #         # TODO "preconds_sum_delta2" function not implemented
        #         min2 = preconds_sum_delta2((p, actions_preconds), result, s)
        #         min3 = preconds_sum_delta2((q, actions_preconds), result, s)
        #         result[(s, (p, q))] = min(min1, min2, min3)

    # compute delta2(s, g). See last line of 12th page of slide.
    delta2_s_g = 0
    for p in g:
        for q in g:
            if p == q:
                continue
            if result[(s, (p, q))] > delta2_s_g:
                delta2_s_g = result[(s, (p, q))]

    result[(s, g)] = delta2_s_g

    return result


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
        print('action function is: ', action, 'action effects: ', effects)
        # delta_out = delta(effects, g, all_cubes)
        delta_out = delta_2(effects, g, all_cubes)
        lambdas.append(effects)
        actions.append(action)
        # delta_with_g.append(delta_out[(tuple(effects), g)])
        delta_with_g.append(delta_out)
    print('actions', actions)
    print('delta', delta_with_g)
    # exit()
    # "while" part of HFS function
    while options:
        # 5th and 6th line of HFS function
        selected_action_index = np.argmin(delta_with_g)
        options.pop(selected_action_index)
        new_a = actions[selected_action_index]
        # print('aaaa: ', a[0])
        # print('next state: ', lambdas[selected_action_index])
        # print('pi is: ', pi + [a[0]])
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
