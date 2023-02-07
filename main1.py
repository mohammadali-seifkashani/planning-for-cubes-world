import numpy as np
from initial import load_initial_state
from operators import operators


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
            result.append((operators.pick_up, cube, pick_up_preconds))
        if type(put_down_preconds) == list:
            result.append((operators.put_down, cube, put_down_preconds))

        for cube2 in all_cubes:
            if cube2 == cube:
                continue
            stack_precons = operators.stack_preconditions(s, cube, cube2)
            unstack_preconds = operators.unstack_preconditions(s, cube, cube2)
            if type(stack_precons) == list:
                result.append((operators.stack, (cube, cube2), stack_precons))
            if type(unstack_preconds) == list:
                result.append((operators.unstack, (cube, cube2), unstack_preconds))

    return result


def renew_options(new_options, options):
    for no in new_options:
        if no not in options:
            options.append(no)


def create_all_p(s, all_cubes):
    result = {(s, 'ARM_EMPTY'): np.inf}

    for cube in all_cubes:
        result[(s, f'CLEAR({cube})')] = np.inf
        result[(s, f'HOLDING({cube})')] = np.inf
        result[(s, f'ON_TABLE({cube})')] = np.inf
        for cube2 in all_cubes:
            if cube2 == cube:
                continue
            result[(s, f'ON({cube}, {cube2})')] = np.inf

    # for simplicity: first we put inf in all predicates (result[s, p] = np.inf).
    # then put 0 in predicates that were in state s previously
    # see first line of implementation of delta function in page 8 of slide
    for p in s:
        result[(s, p)] = 0

    return result


# implementation of delta0(s,p) due to 7th line of delta0 code.
def preconds_sum_delta0(actions_preconds, result, s):
    psd = 1
    for ap in actions_preconds:
        if result[(s, ap)] == np.inf:
            psd = np.inf
            break
        psd += result[(s, ap)]
    return psd


def delta(s, g, all_cubes):
    # see first line of implementation of delta function in page 8 of slide
    # creating all predicates (all p) of delta0 list named "result"
    # TODO maybe we need to add all (p,q) pairs for delta2 too
    result = create_all_p(s, all_cubes)

    # U as the same as implementation of 8th page of slide
    # U will change but s shouldn't change always
    U = s.copy()

    # options = actions
    options = applicable_options(U, all_cubes)  # [(action_function, (action_inputs), action_preconds)]

    for action_function, action_args, actions_preconds in options:
        # TODO functionality for "just_positives" argument isn't implemented yet :)
        # if True, it should return just positive effects of an action
        positive_effects = action_function(*action_args, just_positives=True)

        # in each iteration U will change. 5th line of delta0 code.
        U += positive_effects

        # when U changes, more actions (action = option) are applicable next iteration of U. See 4th line of delta0
        # code. "renew_options" function for this objective.
        new_options = applicable_options(U, all_cubes)
        renew_options(new_options, options)

        # line 6th and 7th of delta0 code
        for p in positive_effects:
            # this is why we needed "actions_preconds" as the 3rd value of tuples of "applicable_options" function.
            psd = preconds_sum_delta0(actions_preconds, result, s)
            result[(s, p)] = min(result[(s, p)], psd)
        # end of delta0 implementation

        # start of delta2 implementation
        for p in positive_effects:
            for q in positive_effects:
                if p == q:
                    continue
                min1 = result[(s, p)]
                # TODO "preconds_sum_delta2" function not implemented
                min2 = preconds_sum_delta2((p, actions_preconds), result, s)
                min3 = preconds_sum_delta2((q, actions_preconds), result, s)
                result[(s, (p, q))] = min(min1, min2, min3)

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
    if satisfies(s, g):
        return pi

    # options = actions
    options = applicable_options(s, all_cubes)

    # list of delta0(lambda(s,a), g) for different actions a
    delta_with_g = []

    # list of lambda(s, a) for different actions a
    lambdas = []

    # 3rd line of HFS function (for delta0)
    # TODO implementation is based on delta0. We need implementation for delta2!
    for action_function, action_args, actions_preconds in options:
        effects = action_function(*action_args, just_positive=False)
        delta_out = delta(effects, g, all_cubes)
        lambdas.append(effects)
        delta_with_g.append(delta_out[(effects, g)])

    # "while" part of HFS function
    while options:
        # 5th and 6th line of HFS function
        selected_action_index = np.argmin(delta_with_g)
        a = options.pop(selected_action_index)

        # 7th line of HFS function
        pi_prime = heuristic_forward_search(pi + [a], lambdas[selected_action_index], g, all_cubes)

        # 8th line of HFS function
        if pi_prime is not False:
            return pi_prime

    # last line of HFS function
    return False


def main():
    pi = []
    s0 = load_initial_state('blocks-world (simplified)/simple.txt')
    print(s0)
    heuristic_forward_search(pi, s0['initial'], s0['goal'], s0['cubes'])
    print(pi)


main()
