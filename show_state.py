from test import get_action_name_and_arguments


def create_columns(s: list, result):
    new_s = []
    for i, p in enumerate(s):
        action_name, arguments = get_action_name_and_arguments(p)
        found = False
        for column in result:
            up = column[-1]
            if arguments[1] == up:
                column.append(arguments[0])
                found = True
                break
        if not found:
            new_s.append(p)

    if new_s:
        return create_columns(new_s, result)
    else:
        return result


def find_downests(s: list, result):
    for p in s:
        action_name, p1arguments = get_action_name_and_arguments(p)
        found = False
        for p2 in s:
            if p == p2:
                continue
            action_name, p2arguments = get_action_name_and_arguments(p2)
            if p1arguments[1] == p2arguments[0]:
                found = True
                break
        if not found and ['#', p1arguments[1]] not in result:
            result.append([p1arguments[1]])


def show_state(s: list):
    s2 = []
    result_list = []
    result = ''
    holding = ''
    for p in s:
        if p.startswith('ON-TABLE'):
            action_name, arguments = get_action_name_and_arguments(p)
            result_list.append(['#', arguments[0]])
        elif p.startswith('HOLDING'):
            action_name, arguments = get_action_name_and_arguments(p)
            holding = f'HOLDING({arguments[0]})'

        if p.startswith('ON('):
            s2.append(p)

    find_downests(s2, result_list)
    result_list = create_columns(s2, result_list)
    result_list = sorted(result_list, key=lambda item: len(item), reverse=True)
    for i in range(len(result_list[0]) - 1, -1, -1):
        for j in range(len(result_list)):
            if i < len(result_list[j]):
                result += result_list[j][i] + '  '
        result += '\n'
    result = result[:-1]
    if holding:
        result += f"\n{holding}\n"
    print(result)


# s = ['ARM-EMPTY', 'CLEAR(a)', 'ON-TABLE(c)', 'ON(b,c)', 'ON(a,b)', 'ON-TABLE(d)', 'ON(x,d)']
# show_state(s)
