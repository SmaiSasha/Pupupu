import sys
from dataclasses import dataclass, field
from collections import defaultdict

# Описание состояния (final - флаг конечного состояния, transitions - словарь переходов)
@dataclass
class StateDesc:
    final: bool = False
    transitions: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

# Тип для представления автомата
type StateMachine = dict[str, StateDesc]

# Константы
EPSILON = "ε"  # Символ эпсилон-перехода
STATE_PREFIX = "S"  # Префикс для названий новых состояний
START_STATE_INDEX = 0  # Индекс начального состояния


# Функция чтения конечного автомата из CSV файла
def read_state_machine(file_name: str) -> tuple[StateMachine, str, str]:
    """
    Считывает конечный автомат из файла CSV и возвращает автомат, начальное и конечное состояние.
    """
    with open(file_name, "r", encoding="utf-8") as f:
        data = f.read().splitlines()
    
    state_machine: dict[str, StateDesc] = defaultdict(StateDesc)
    final_symbols = data[0].strip().split(";")
    states = data[1].strip().split(";")
    start_state = states[1]
    final_state = states[final_symbols.index("F")]
    
    for line in data[2:]:
        if not line.strip(): 
            continue

        line = line.strip().split(";")
        symbol = line[0]
        
        for i, transition in enumerate(line[1:], start=1):
            transition = transition.strip()
            state_machine[states[i]].final = final_state == states[i]
            state_machine[states[i]].transitions[symbol] = transition.split(",") if transition else []
    
    return state_machine, start_state, final_state


# Получение всех эпсилон-переходов для каждого состояния
def get_epsilon_transitions(state_machine: StateMachine) -> dict:
    """
    Возвращает словарь эпсилон-переходов для каждого состояния.
    """
    transitions = {}
    states = list(state_machine.keys())
    
    for state in states:
        visited, queue = [], [state]
        while queue:
            s = queue.pop()
            if s not in visited:
                visited.append(s)
                queue.extend(state_machine[s].transitions.get(EPSILON, []))

        transitions[state] = visited[:]

    return transitions


# Построение e-closure (замыкания) для множества состояний
def eclosure(states, epsilon_transitions) -> list:
    """
    Возвращает e-closure (замыкание) для заданного множества состояний.
    """
    eclosures_list = list()
    for state in states:
        eclosures_list.extend([state] + epsilon_transitions[state])

    return list(dict.fromkeys(eclosures_list))


# Получение переходов по символу из e-closure
def get_transitions_for_state(current_eclosure: list, symbol: str, state_machine: StateMachine) -> list[str]:
    """
    Возвращает переходы для текущего замыкания по заданному символу.
    """
    transitions = []
    for s in current_eclosure:
        transitions.extend(state_machine[s].transitions[symbol])
    return list(dict.fromkeys(transitions))


# Поиск или создание нового состояния для текущих переходов
def find_or_create_state(transitions: list[str], states_eclosures: dict[str, list[str]], states: list[str]) -> str:
    """
    Возвращает существующее состояние для данных переходов или создаёт новое.
    """
    if not transitions:
        return ''
        
    for k, v in states_eclosures.items():
        if sorted(transitions) == sorted(v):
            return k
        
    new_state = f"{STATE_PREFIX}{len(states)+START_STATE_INDEX}"
    states.append(new_state)
    states_eclosures[new_state] = transitions
    return new_state


# Преобразование НКА в ДКА
def determine_state_machine(state_machine: StateMachine, start_state: str, final_state: str) -> StateMachine:
    """
    Преобразует недетерминированный конечный автомат (НКА) в детерминированный (ДКА).
    """
    epsilon_transitions = get_epsilon_transitions(state_machine)
    states_eclosures = {f"{STATE_PREFIX}{START_STATE_INDEX}": [start_state]}
    states_to_process = [f"{STATE_PREFIX}{START_STATE_INDEX}"]
    determined_state_machine: StateMachine = defaultdict(StateDesc)

    for state in states_to_process:
        current_eclosure = eclosure(states_eclosures[state], epsilon_transitions)
        determined_state_machine[state].final = final_state in current_eclosure

        for symbol in state_machine[start_state].transitions:
            if symbol == EPSILON: continue

            transitions = get_transitions_for_state(current_eclosure, symbol, state_machine)
            next_state = find_or_create_state(transitions, states_eclosures, states_to_process)
            determined_state_machine[state].transitions[symbol] = [next_state]

    return determined_state_machine


def minimize_dfa(state_machine: StateMachine, start_state: str) -> tuple[StateMachine, str]:
    """
    Минимизирует детерминированный конечный автомат (ДКА).
    Возвращает минимизированный автомат и новое начальное состояние.
    """
    # Шаг 1: Разделение на финальные и нефинальные состояния
    final_states = {state for state in state_machine if state_machine[state].final}
    non_final_states = set(state_machine.keys()) - final_states

    # Начальное разбиение (финальные и нефинальные состояния)
    partitions = [final_states, non_final_states]
    states_to_partition = {state: 0 if state in final_states else 1 for state in state_machine}

    def get_partition_key(state, symbol):
        """Возвращает ключ разбиения для перехода по символу."""
        next_state = state_machine[state].transitions.get(symbol, [""])[0]
        return states_to_partition.get(next_state, -1)

    # Шаг 2: Итеративное уточнение разбиений
    while True:
        new_partitions = []
        for group in partitions:
            if not group:  # Пропускаем пустые группы
                continue
            # Разделяем группу на подгруппы
            subgroups = defaultdict(set)
            for state in group:
                transition_key = tuple(get_partition_key(state, symbol) for symbol in state_machine[state].transitions)
                subgroups[transition_key].add(state)
            new_partitions.extend(subgroups.values())

        # Если разбиения не изменились, завершаем
        if len(new_partitions) == len(partitions):
            break

        partitions = new_partitions
        states_to_partition = {state: i for i, group in enumerate(partitions) for state in group}

    # Шаг 3: Создание нового автомата
    minimized_state_machine: StateMachine = defaultdict(StateDesc)
    state_mapping = {state: f"{STATE_PREFIX}{i}" for i, group in enumerate(partitions) if group for state in group}

    for group in partitions:
        if not group:  # Пропускаем пустые группы
            continue
        repr_state = next(iter(group))  # Представитель группы
        new_state = state_mapping[repr_state]
        minimized_state_machine[new_state].final = state_machine[repr_state].final
        for symbol, targets in state_machine[repr_state].transitions.items():
            if targets and targets[0] in state_mapping:  # Проверяем, что цель перехода не пуста и есть в state_mapping
                minimized_state_machine[new_state].transitions[symbol] = [state_mapping[targets[0]]]

    new_start_state = state_mapping[start_state]
    return minimized_state_machine, new_start_state




# Сохранение конечного автомата в файл CSV
def save_state_machine(state_machine: StateMachine, file_name: str) -> None:
    """
    Сохраняет конечный автомат в формате CSV.
    """
    symbols = sorted({symbol for state in state_machine for symbol in state_machine[state].transitions})
    f_line = [""] + ["F" if state_machine[state].final else '' for state in state_machine]
    states_line = [""] + list(state_machine.keys())

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(';'.join(f_line) + "\n")
        f.write(';'.join(states_line) + "\n")
        for symbol in symbols:
            transitions = [state_machine[state].transitions[symbol][0] for state in states_line[1:]]
            f.write(';'.join([symbol] + transitions) + "\n")


# Главная функция
def main():
    """
    Главная функция для выполнения преобразования НКА в ДКА.
    """
    state_machine, start_state, final_state = read_state_machine(sys.argv[1])
    determined_state_machine = determine_state_machine(state_machine, start_state, final_state)
    minimized_state_machine, minimized_start_state = minimize_dfa(determined_state_machine, f"{STATE_PREFIX}{START_STATE_INDEX}")
    save_state_machine(minimized_state_machine, sys.argv[2])


# Точка входа
if __name__ == "__main__":
    main()
