import re
import sys

def read_and_parse_grammar(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        grammar = {}
        grammar_type = None  # 'left' or 'right'

        left_regex = re.compile(r"^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$")
        right_regex = re.compile(r"^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$")
        
        current_line = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            current_line += " " + line
            if line[-1] == "|":
                continue

            left_match = left_regex.match(current_line)
            right_match = right_regex.match(current_line)

            if grammar_type == None:
                if left_match and right_match:
                    current_line = ""
                    continue
                if left_match:
                    grammar_type = 'left'
                    break
                elif right_match:
                    grammar_type = 'right'
                    break
            
        if grammar_type == None:
            grammar_type = 'right'

        current_line = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            current_line += " " + line
            if line[-1] == "|":
                continue

            left_match = left_regex.match(current_line)
            right_match = right_regex.match(current_line)

            if grammar_type == 'left':
                head, productions = left_match.groups()

            elif grammar_type == 'right':
                head, productions = right_match.groups()

            # Split productions and add them to the grammar dictionary
            production_list = [prod.strip() for prod in productions.split('|')]
            if head not in grammar:
                grammar[head] = []
            grammar[head].extend(production_list)
            current_line = ""

        return grammar, grammar_type

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def build_state_graph(grammar, grammar_type):
    state_mapping = {}
    transitions = {}
    final_states = set()

    if grammar_type == 'left':
        state_mapping['S'] = 'q0'
        i=0
        for key in grammar:
            state_mapping[key] = 'q' + str(len(grammar) - i)
            i +=1
            transitions[state_mapping[key]] = {}
        final_states.add('q' + str(len(grammar)))
        transitions["q0"] = {}
        for key in grammar:
            for transition in grammar[key]:
                transition = transition.split()
                if len(transition) == 2:
                    if transition[1] in transitions[state_mapping[transition[0][1:-1]]]:
                        transitions[state_mapping[transition[0][1:-1]]][transition[1]] += "," + state_mapping[key]    
                    else:
                        transitions[state_mapping[transition[0][1:-1]]][transition[1]] = state_mapping[key]
                else:
                    if transition[0] in transitions["q0"]:
                        transitions["q0"][transition[0]] += state_mapping[key]
                    else:
                        transitions["q0"][transition[0]] = state_mapping[key]
    elif grammar_type == 'right':
        state_mapping['F'] = "q" + str(len(grammar))
        i=0
        for key in grammar:
            state_mapping[key] = 'q' + str(i)
            i += 1
            transitions[state_mapping[key]] = {}
        final_states.add('q' + str(len(grammar)))
        transitions['q' + str(len(grammar))] = {}
        for key in grammar:
            for transition in grammar[key]:
                transition = transition.split()
                if len(transition) == 2:
                    if transition[0] in transitions[state_mapping[key]]:
                        transitions[state_mapping[key]][transition[0]] += "," + state_mapping[transition[1][1:-1]]
                    else:
                        transitions[state_mapping[key]][transition[0]] =  state_mapping[transition[1][1:-1]]
                else:
                    if transition[0] in transitions[state_mapping[key]]:
                        transitions[state_mapping[key]][transition[0]] += "," "q" + str(len(grammar))
                    else:
                        transitions[state_mapping[key]][transition[0]] = "q" + str(len(grammar))

    return state_mapping, transitions, final_states




def generate_output_table(transitions, final_states):
    # Список всех состояний
    states = list(transitions.keys())
    states.sort()  # Упорядочим для предсказуемого вывода

    # Создаём заголовки таблицы
    final_state_row = ["" for _ in states]
    final_state_row.append("")
    for idx, state in enumerate(states):
        if state in final_states:
            final_state_row[idx + 1] = "F"

    # Заголовок с состояниями
    header_row = [""] + states

    # Генерация строк с переходами
    transition_rows = []
    for terminal in sorted({t for state in states for t in transitions.get(state, {})}):
        row = [terminal]  # Первая колонка — терминал
        for state in states:
            if terminal in transitions.get(state, {}):
                targets = transitions[state][terminal]
                if not isinstance(targets, list):
                    targets = [targets]
                row.append(",".join(sorted(targets)))
            else:
                row.append("")
        transition_rows.append(row)

    # Генерация финальной таблицы
    output_table = [";".join(final_state_row), ";".join(header_row)]
    for row in transition_rows:
        output_table.append(";".join(row))

    return "\n".join(output_table)


# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    grammar, grammar_type = read_and_parse_grammar(input_file)

    state_mapping, transitions, final_states = build_state_graph(grammar, grammar_type)

    table = generate_output_table(transitions, final_states)

    # Write table to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(table)

    print(f"Output written to {output_file}")
