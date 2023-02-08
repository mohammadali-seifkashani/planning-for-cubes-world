def get_action_name_and_arguments(p):
    paranthesis_index = p.find('(')
    action_name = p[:paranthesis_index]
    arguments = p[paranthesis_index + 1: -1].split(',')
    return action_name, arguments


def make_test(cubes: list, s: list, g: list):
    result = f'OBJECTS:{len(cubes)}\n'
    result += '\n'.join(cubes) + '\n\n\n'

    result += f'INITIAL-STATE:{len(s)}\n'
    for p in s:
        if p == 'ARM-EMPTY':
            result += 'ARM-EMPTY\n'
        else:
            action_name, arguments = get_action_name_and_arguments(p)
            result += action_name + '\n'
            if len(arguments) == 1:
                result += arguments[0] + '\n'
            else:
                result += '\n'.join(arguments) + '\n'

    result += f'\n\nGOALS:{len(g)}\n'
    for p in g:
        if p == 'ARM-EMPTY':
            result += 'ARM-EMPTY\n'
        else:
            action_name, arguments = get_action_name_and_arguments(p)
            result += action_name + '\n'
            if len(arguments) == 1:
                result += arguments[0] + '\n'
            else:
                result += '\n'.join(arguments) + '\n'

    f = open('our_tests/test1.txt', 'w')
    f.write(result)
    f.close()
    return result


# r = make_test(
#     ['a', 'b', 'c'],
#     ['ARM-EMPTY', 'CLEAR(a)', 'ON-TABLE(c)', 'ON(b,c)', 'ON(a,b)'],
#     ['ON-TABLE(a)', 'ON(b,a)', 'CLEAR(b)']
# )
# print(r)
