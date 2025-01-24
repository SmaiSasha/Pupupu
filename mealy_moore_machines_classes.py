PYVIS_OPTIONS = """
        var options = {
          "nodes": {
            "font": {
              "size": 16
            },
            "shape": "ellipse"
          },
          "edges": {
            "arrows": {
              "to": {
                "enabled": true
              }
            },
            "font": {
              "size": 12
            }
          },
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -100000,
              "centralGravity": 0.3,
              "springLength": 95
            }
          }
        }
        """
class mealey_machine:
    def __init__(self, states, inputs, transitions, start_state):
        """
        Инициализация автомата Мили.

        :param states: Набор состояний автомата Мили.
        :param inputs: Набор входных символов.
        :param transitions: Функция переходов автомата Мили (словарь), которая определяет следующее состояние и выходной символ для
                            каждого состояния и входного символа.
        """
        self.states = states
        self.inputs = inputs
        self.transitions = transitions
        self.start_state = start_state

    def from_file(file_path: str):
        """
        Парсинг файла автомата Мили и преобразование его в структуры данных для MealyMachine.
        :param file_path: Путь к файлу с таблицей автомата Мили.
        :return: Кортеж, содержащий (states, inputs, transitions, outputs), которые можно использовать для инициализации MealyMachine.
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Разделение строк на ячейки по разделителю ";"
        parsed_lines = [line.strip().split(';') for line in lines]

        # Первая строка - это состояния (s0, s1, s2, ...)
        states = parsed_lines[0][1:]  # Пропускаем первый пустой элемент (так как перед ';' ничего нет)
        start_state = states[0]
        # Входные значения - это первый столбец (x1, x2, x3, ...)
        inputs = [line[0] for line in parsed_lines[1:]]

        # Инициализируем словари для переходов и выходов
        transitions = {}

        # Проходим по всем строкам (кроме заголовка) и обрабатываем каждую ячейку
        for i, input_symbol in enumerate(inputs):
            for j, state in enumerate(states):
                transition_output = parsed_lines[i + 1][j + 1]
                next_state, output = transition_output.split('/')  # Разделение состояния и выхода по символу "/"
                
                # Заполняем переходы и выходы для автомата Мили
                transitions[(state, input_symbol)] = (next_state, output)
        return mealey_machine(states, inputs, transitions, start_state)
    
    def mealey_to_moore(mealy_machine):
        moore_states_unnum = []
        for i in mealy_machine.transitions:
            moore_states_unnum.append(mealy_machine.transitions[i]) 
        moore_states_unnum = list(set(moore_states_unnum))
        moore_states_unnum.sort()
        moore_states = []
        i = 0
        j = 0
        temp_moore_outputs_mapping = {}
        moore_outputs_mapping = {}
        for state in mealy_machine.states:
          if state == moore_states_unnum[j][0]:
            while (j < len(moore_states_unnum)) and (state == moore_states_unnum[j][0]):
              moore_states.append("q" + str(i))
              temp_moore_outputs_mapping[moore_states[i]] = moore_states_unnum[j]
              moore_outputs_mapping[moore_states[i]] = moore_states_unnum[j][1]
              i+=1
              j+=1
          else:
            moore_states.append("q" + str(i))
            temp_moore_outputs_mapping[moore_states[i]] = (state, '-')
            moore_outputs_mapping[moore_states[i]] =  '-'
            i+=1
        moore_inputs = mealy_machine.inputs
        moore_transitions = {}
        for state in moore_states:
            for inpt in moore_inputs:
                transition = list(temp_moore_outputs_mapping.keys())[list(temp_moore_outputs_mapping.values()).index(mealy_machine.transitions[(temp_moore_outputs_mapping[state][0], inpt)])]
                moore_transitions[(state, inpt)] = transition
        return moore_states, moore_inputs, moore_transitions, moore_outputs_mapping
    
    def visualize(self):
        """
        Визуализация автомата Мили с помощью библиотеки PyVis.
        """
        # Импортируем Network только при необходимости
        from pyvis.network import Network
        
        # Создаем объект сети
        net = Network(directed=True)  # directed=True указывает, что это ориентированный граф

        # Добавляем узлы - это состояния Mealy-машины
        for state in self.states:
            net.add_node(state, label=state, title=f"State: {state}")

        # Добавляем рёбра - это переходы с метками (вход/выход)
        for (state, input_signal), (next_state, output_signal) in self.transitions.items():
            # Метка ребра будет выглядеть как 'x1/y1' (вход/выход)
            edge_label = f"{input_signal}/{output_signal}"
            net.add_edge(state, next_state, label=edge_label, title=edge_label)

        # Настройка внешнего вида сети
        net.set_options(PYVIS_OPTIONS)
        
        # Сохраняем и отображаем граф
        net.show("mealy_machine.html", notebook=False)

    def return_as_table(self):
      # Сначала создаём первую строку - заголовок с состояниями
      table_str = ";" + ";".join(self.states) + "\n"

      # Теперь проходим по каждому входному сигналу
      for input_signal in self.inputs:
          row = [input_signal]  # Начало строки с сигналом входа
          for state in self.states:
              # Для каждого состояния ищем переход для данного входного сигнала
              next_state, output = self.transitions[(state, input_signal)]
              # Формируем запись в формате next_state/output
              row.append(f"{next_state}/{output}")
          # Добавляем строку в таблицу
          table_str += ";".join(row) + "\n"

      return table_str
    
    def minimize(self):
        # Шаг 1: Нахождение достижимых состояний
        reachable_states = set()
        queue = [self.start_state]
        while queue:
            current_state = queue.pop(0)
            if current_state not in reachable_states:
                reachable_states.add(current_state)
                # Добавляем в очередь все состояния, в которые можно перейти из текущего
                for input_symbol in self.inputs:
                    next_state = self.transitions[(current_state, input_symbol)][0]
                    if next_state not in reachable_states:
                        queue.append(next_state)

        # Убираем недостижимые состояния из списка состояний и переходов
        reachable_transitions = {
            (state, input_symbol): (next_state, output_symbol)
            for (state, input_symbol), (next_state, output_symbol) in self.transitions.items()
            if state in reachable_states and next_state in reachable_states
        }
        reachable_states = list(reachable_states)
        # Шаг 2: Инициализация таблицы эквивалентности
        equivalence_table = {}
        for i, state1 in enumerate(reachable_states):
            for j, state2 in enumerate(reachable_states):
                if i < j:
                    equivalence_table[(state1, state2)] = None  # Изначально состояния считаются эквивалентными

        # Шаг 3: Проверка эквивалентности на основе выходных символов
        for (state1, state2) in equivalence_table:
            for input_symbol in self.inputs:
                output1 = reachable_transitions[(state1, input_symbol)][1]
                output2 = reachable_transitions[(state2, input_symbol)][1]
                if output1 != output2:
                    equivalence_table[(state1, state2)] = False  # Помечаем как неэквивалентные
                    break  # Достаточно одного различия

        # Шаг 4: Итеративная проверка эквивалентности на основе переходов
        changes = True
        while changes:  # Повторяем, пока происходят изменения
            changes = False
            for (state1, state2) in equivalence_table:
                if equivalence_table[(state1, state2)] is None:  # Если состояния пока эквивалентны
                    for input_symbol in self.inputs:
                        next_state1 = reachable_transitions[(state1, input_symbol)][0]
                        next_state2 = reachable_transitions[(state2, input_symbol)][0]

                        # Проверяем их эквивалентность по переходам
                        if next_state1 != next_state2:
                            if (min(next_state1, next_state2), max(next_state1, next_state2)) in equivalence_table:
                                if equivalence_table[(min(next_state1, next_state2), max(next_state1, next_state2))] is False:
                                    equivalence_table[(state1, state2)] = False  # Если переходы ведут в неэквивалентные состояния
                                    changes = True
                                    break

        # Шаг 5: Группировка эквивалентных состояний
        equivalent_states = {}
        for (state1, state2), is_equivalent in equivalence_table.items():
            if is_equivalent is None:  # Эквивалентные состояния
                if state1 not in equivalent_states and state2 not in equivalent_states:
                    equivalent_states[state1] = state1
                    equivalent_states[state2] = state1
                elif state1 in equivalent_states:
                    equivalent_states[state2] = equivalent_states[state1]
                elif state2 in equivalent_states:
                    equivalent_states[state1] = equivalent_states[state2]

        # Для остальных состояний, которые не были затронуты (не объединены)
        for state in reachable_states:
            if state not in equivalent_states:
                equivalent_states[state] = state

        # Шаг 6: Формирование новой таблицы переходов
        new_states = list(set(equivalent_states.values()))  # Получаем уникальные эквивалентные состояния
        new_transitions = {}

        for (state, input_symbol), (next_state, output_symbol) in reachable_transitions.items():
            minimized_state = equivalent_states[state]
            minimized_next_state = equivalent_states[next_state]
            new_transitions[(minimized_state, input_symbol)] = (minimized_next_state, output_symbol)

        # Шаг 7: Возврат минимизированных атрибутов
        return mealey_machine(new_states, self.inputs, new_transitions, equivalent_states[self.start_state])


class moore_machine:
    def __init__(self, states, inputs, transitions, output_mapping):
        """
        Инициализация автомата Мура.

        :param states: Набор состояний автомата Мура.
        :param inputs: Набор входных символов.
        :param transitions: Функция переходов автомата Мура (словарь), которая определяет следующее состояние для
                            каждого состояния и входного символа.
        :param output_mapping: Функция, которая сопоставляет состояниям автомата Мура соответствующие выходные символы.
        """
        self.states = states
        self.inputs = inputs
        self.transitions = transitions
        self.output_mapping = output_mapping
    
    def from_file(file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
        # Разделяем строки и удаляем лишние пробелы
        parsed_lines = [line.strip().split(";") for line in lines]

        # Первая строка - выходные значения
        output_mapping_values = parsed_lines[0][1:]

        # Вторая строка - состояния
        states = parsed_lines[1][1:]

        # Остальные строки - входы и переходы
        inputs = [line[0] for line in parsed_lines[2:]]
        transitions_data = [line[1:] for line in parsed_lines[2:]]

        # Составляем таблицу переходов
        transitions = {}
        for i, input_signal in enumerate(inputs):
            for j, state in enumerate(states):
                transitions[(state, input_signal)] = transitions_data[i][j]

        # Составляем выходные значения для каждого состояния
        output_mapping = {state: output_mapping_values[i] for i, state in enumerate(states)}
        return moore_machine(states, inputs, transitions, output_mapping)
    
    def moore_to_mealey(moore_machine):
        # Извлекаем состояния, входы, переходы и отображение выходов из moore_machine
        moore_states = moore_machine.states
        moore_inputs = moore_machine.inputs
        moore_transitions = moore_machine.transitions
        moore_output_mapping = moore_machine.output_mapping

        # Готовим структуру для хранения переходов Mealy-машины
        mealey_transitions = {}

        # Проходим по всем состояниям и входам
        for state in moore_states:
            for input_signal in moore_inputs:
                # Определяем новое состояние, в которое переходит машина при данном входе
                new_state = moore_transitions[(state, input_signal)]

                # Для Mealy-машины нужно также получить выход на переходе, который соответствует выходу нового состояния в Moore-машине
                output_signal = moore_output_mapping[new_state]

                # Добавляем в таблицу переходов для Mealy-машины: текущий state, вход и переход в новую state с соответствующим выходом
                mealey_transitions[(state, input_signal)] = (new_state, output_signal)
        return moore_states, moore_inputs, mealey_transitions
    
    def visualize(self):
        from pyvis.network import Network
        # Создаем сетевой граф для визуализации
        net = Network(directed=True)

        # Добавляем узлы (состояния) с выходами
        for state in self.states:
            label = f"{state}/{self.output_mapping[state]}"  # Метка: состояние/выход
            net.add_node(state, label=label)

        # Добавляем рёбра (переходы) с метками входных сигналов
        for (state, input_signal), next_state in self.transitions.items():
            net.add_edge(state, next_state, label=input_signal)  # Метка ребра — входной сигнал

        # Настройки для визуализации
        net.set_options(PYVIS_OPTIONS)

        # Сохранение графа в HTML-файл
        net.show("moore_machine.html", notebook=False)
    
    def return_as_table(self):
      # Формируем первую строку с выходами (output_mapping)
      outputs = ";" + ";".join([self.output_mapping[state] for state in self.states]) + "\n"
      
      # Формируем вторую строку с состояниями
      states = ";" + ";".join(self.states) + "\n"

      # Формируем строки для каждого входного сигнала
      transitions = ""
      for input_signal in self.inputs:
          row = [input_signal]  # Начинаем строку с входного сигнала
          for state in self.states:
              # Добавляем состояние-переход для данного входного сигнала
              next_state = self.transitions[(state, input_signal)]
              row.append(next_state)
          transitions += ";".join(row) + "\n"  # Преобразуем список строки в строку и добавляем её в общие переходы

      # Складываем все части таблицы
      table_str = outputs + states + transitions
      return table_str
    
    def minimize(self):
        # Шаг 1: Классификация состояний по выходным символам
        groups = {}
        for state in self.states:
            output = self.output_mapping[state]
            if output not in groups:
                groups[output] = []
            groups[output].append(state)

        # Превращаем группы в список списков
        partition = list(groups.values())

        # Шаг 2: Построение таблицы переходов
        def get_transition_class(state, input_symbol, current_partition):
            next_state = self.transitions[(state, input_symbol)]
            for group in current_partition:
                if next_state in group:
                    return current_partition.index(group)
            return -1

        # Шаг 3-4: Итеративное разбиение групп
        stable = False
        while not stable:
            new_partition = []
            for group in partition:
                # Разбиение группы
                subgroups = {}
                for state in group:
                    transition_signature = tuple(get_transition_class(state, input_symbol, partition) for input_symbol in self.inputs)
                    if transition_signature not in subgroups:
                        subgroups[transition_signature] = []
                    subgroups[transition_signature].append(state)

                # Добавляем все полученные подгруппы
                new_partition.extend(subgroups.values())

            # Проверяем, изменилась ли структура групп
            if new_partition == partition:
                stable = True
            else:
                partition = new_partition

        # Шаг 5: Построение минимизированного автомата
        minimized_states = ['s' + str(i) for i in range(len(partition))]
        minimized_transitions = {}
        minimized_output_mapping = {}

        for i, group in enumerate(partition):
            representative_state = group[0]
            minimized_output_mapping[minimized_states[i]] = self.output_mapping[representative_state]

            # Заполняем переходы для нового состояния
            for input_symbol in self.inputs:
                next_state = self.transitions[(representative_state, input_symbol)]
                for j, group in enumerate(partition):
                    if next_state in group:
                        minimized_transitions[(minimized_states[i], input_symbol)] = minimized_states[j]
                        break

        # Возвращаем минимизированные атрибуты
        return moore_machine(minimized_states, self.inputs, minimized_transitions, minimized_output_mapping)