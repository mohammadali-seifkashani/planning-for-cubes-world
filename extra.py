import numpy as np
from main import create_all_p, applicable_options, get_state_goal_delta


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


def delta(s, g, all_cubes):
    result = create_all_p(s, all_cubes)
    U = s.copy()
    while True:
        new_U, new_result = update_delta(s, result, U, all_cubes)
        if result == new_result:
            # print('final result: ', result)
            goal_distance = get_state_goal_delta(s, g, result)
            break
        else:
            U = new_U
            result = new_result
    # print(goal_distance)
    return goal_distance


