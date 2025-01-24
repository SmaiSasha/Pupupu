from mealy_moore_machines_classes import mealey_machine, moore_machine
import sys



# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <mealy/moore> <input_file> <output_file>")
        sys.exit(1)
    macnine_type = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    if macnine_type == "mealy":
        mealey = mealey_machine.from_file(input_file)
        min_mealey = mealey.minimize()
        table = min_mealey.return_as_table()
    elif macnine_type == "moore":
        moore = mealey_machine.from_file(input_file)
        min_moore = moore.minimize()
        table = min_moore.return_as_table()

    # Write table to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(table)

    print(f"Output written to {output_file}")


# moore_states, moore_inputs, moore_transitions, moore_outputs_mapping = mealey_machine.mealey_to_moore(mealey)
# moore = moore_machine(moore_states, moore_inputs, moore_transitions, moore_outputs_mapping)

# moore_2 = moore_machine.from_file('input_moore.txt')
# moore_2.visualize()

# min_moore = moore_2.minimize()
# # print('mealy.states:', mealey.states)
# # print('mealy.inputs:', mealey.inputs)
# # print('mealey.transitions:', mealey.transitions)

# # print('states:', min_mealey.states)
# # print('inputs:', min_mealey.inputs)
# # print('transitions:', min_mealey.transitions)
# print(min_moore.return_as_table())

# moore_2 = moore_machine.from_file('input_moore.txt')
# mealey_states, mealey_inputs, mealey_transitions = moore_machine.moore_to_mealey(moore_2)
# mealey_2 = mealey_machine(mealey_states, mealey_inputs, mealey_transitions)

# print(moore_2.return_as_table())

# mealey_2.visualize()



# print('mealy_2.states:', mealey_2.states)
# print('mealy_2.inputs:', mealey_2.inputs)
# print('mealey_2.transitions:', mealey_2.transitions)

# print('mealy.states:', mealey_2.states == mealey.states)
# print('mealy.inputs:', mealey_2.inputs == mealey.inputs)
# print('mealey.transitions:', mealey_2.transitions == mealey.transitions)

# print('moore.states:',moore.states)
# print('moore.inputs:',moore.inputs)
# print('moore.transitions:',moore.transitions)
# print('moore.output_mapping;',moore.output_mapping)

# print('moore_2.states:',moore_2.states)
# print('moore_2.inputs:',moore_2.inputs)
# print('moore_2.transitions:',moore_2.transitions)
# print('moore_2.output_mapping:',moore_2.output_mapping)

#   ;  s0   ; s1   ; s2   ; s3
# x1; s3/y1; s0/y2; s2/y3; s0/y5
# x2; s1/y1; s2/y1; s0/y4; s3/y2
# x3; s0/y2; s1/y4; s3/y1; s1/y5


# q0 s0/y2
# q1 s0/y4
# q2 s0/y5
# q3 s1/y1
# q4 s1/y4
# q5 s1/y5
# q6 s2/y1
# q7 s2/y3
# q8 s3/y1
# q9 s3/y2


#   ;y2;y4;y5;y1;y4;y5;y1;y3;y1;y2
#   ;q0;q1;q2;q3;q4;q5;q6;q7;q8;q9
# x1;q8;q8;q8;q0;q0;q0;q7;q7;q2;q2
# x2;q3;q3;q3;q6;q6;q6;q1;q1;q9;q9
# x3;q2;q2;q2;q4;q4;q4;q8;q8;q5;q5


# 	Мур:
#   ;y2;y4;y5;y1;y4;y5;y1;y3;y1;y2
#   ;q0;q1;q2;q3;q4;q5;q6;q7;q8;q9
# x1;q8;q8;q8;q0;q0;q0;q7;q7;q2;q2
# x2;q3;q3;q3;q6;q6;q6;q1;q1;q9;q9
# x3;q2;q2;q2;q4;q4;q4;q8;q8;q5;q5

# Мили:
#   ;  q0;    q1;    q2;    q3;    q4;    q5;    q6;    q7;    q8;    q9
# x1; q8/y1; q8/y1; q8/y1; q0/y2; q0/y2; q0/y2; q7/y3; q7/y3; q2/y5; q2/y5
# x2; q3/y1; q3/y1; q3/y1; q6/y1; q6/y1; q6/y1; q1/y4; q1/y4; q9/y2; q9/y2
# x3; q2/y5; q2/y5; q2/y5; q4/y4; q4/y4; q4/y4; q8/y1; q8/y1; q5/y5; q5/y5






