import json

def accuracy_opt_passes_optimization(options, program) :
    f = open(options.llm, 'r', encoding='utf-8')
    llm = f.read()
    f.close()

    for line_count, _ in enumerate(program.statements) :
        print(program.statements[line_count])

    return program.statements