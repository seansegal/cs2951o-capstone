import math
import argparse
import random
import time
from parser import parse_input_walk_sat

def walkSAT(model, clauses,var_to_clauses, p_random_step):
    """
    Performs stochastic local search to determine whether a file in cnf format is SAT or UNSAT.
    Input: model - a dictionary of variables to booleans
           clauses - a list of all clauses
           var_to_clauses - a dictionary of variables to the clauses that contain that variable
           p_random_step - a float representing a probability with we shoudld perform a flip
    Output: False - if the expression is UNSAT
            model - a dictionary of the model in the case of SAT
    """
    unsatisfied_clauses = get_unsatisfied_clauses(model, clauses)
    itercount = 0
    previous_seen_models = set()
    while len(unsatisfied_clauses) > 0:
        if itercount == 500000: # declare UNSAT if we have gone through 500000 iterations this could be increased
                                # for harder SAT problems
            return False
        itercount += 1
        random_index = random.randint(0, (len(unsatisfied_clauses)-1))
        unsatisfied_clause = unsatisfied_clauses[random_index] # getting a random clause
        uniform_sample = random.random()
        if uniform_sample < p_random_step: # with probability P we select a variable to flip
            random_index = random.randint(0, (len(unsatisfied_clause)-1))
            var_to_flip = abs(unsatisfied_clause[random_index])
        else:
            var_to_flip = abs(get_best_var(model, var_to_clauses,unsatisfied_clause)[0]) # get maximizing variable

        model[var_to_flip] = not model[var_to_flip] # flipping variable
        current_model = model_to_binary(model)
        new_clauses = []
        new_clauses = new_clauses + var_to_clauses[var_to_flip]
        if current_model in previous_seen_models: # keep flipping if the model has been previously seen
            for v in unsatisfied_clause:
                if int(math.fabs(v)) != var_to_flip:
                    model[int(math.fabs(v))] = not model[int(math.fabs(v))]
                    new_clauses = new_clauses + var_to_clauses[int(math.fabs(v))]
                    current_model = model_to_binary(model)
                    if current_model not in previous_seen_models:
                        break
        previous_seen_models.add(current_model)
        clauses_to_check = unsatisfied_clauses + new_clauses
        unsatisfied_clauses = get_unsatisfied_clauses(model, clauses_to_check)

    return model

def get_best_var(model, var_to_clauses, unsatisfied_clause):
    """
    returns maximizing variable to flip that decreases the number of unsatisfied clauses
    Input:   model -  a dictionary of variables to booleans
             var_to_clauses - a dictionary of variables to the clauses that contain that variable
             unsatsified_clause - a list of variables
    Output: max_var maximizing variables
    """
    max_var = (0, -float("inf"))
    uniform_sample = random.random()
    for var in unsatisfied_clause:
        value = model[int(math.fabs(var))]
        number_satisfied_by_flipping = 0
        for c in var_to_clauses[int(math.fabs(var))]:
            if value:
                if -var in c:
                    number_satisfied_by_flipping +=1
            else:
                if var in c:
                    number_satisfied_by_flipping +=1
        if number_satisfied_by_flipping > max_var[1]:
            max_var = (var, number_satisfied_by_flipping)

    return max_var

def model_to_binary(model):
    """
    returns model as a binary string
    Input: model - a dictionary of variables to booleans
    Output: binary_string - a binary string representing the variables
    """
    binary_string = ''
    for _, v in model.iteritems():
        if v:
            binary_string += '1'
        else:
            binary_string += '0'
    return binary_string

def get_unsatisfied_clauses(model, clauses):
    """
    creates a list of unsatisfied caluses
    Inputs: model -  a dictionary of variables to booleans
            clauses -  a list of all clauses
    Output: unsatisfied_clauses - a list of unsatisfied clauses
    """
    unsatisfied_clauses = []
    for c in clauses:
        if clause_value(c, model) is False:
            unsatisfied_clauses.append(c)
    return unsatisfied_clauses

def clause_value(clause, model):
    """
    returns the values of a clause
    Inputs: clause - a list of variables
            model -  a dictionary of variables to booleans
    Output: boolean
    """
    for literal in clause:
        v = int(math.fabs(literal))
        if v in model and literal_true_in_model(literal, model):
            return True
    return False

def literal_true_in_model(l, model):
    """
    returns True if the literal is True in the clause and False otherwise
    Input: l - a literal
           model - a dictionary of variables to booleans
    Output: boolean
    """
    if l > 0 and model[l] or l < 0 and not model[-l]:
        return True
    return False

def add_to_list_in_dict(dic, key, value):
    if key in dic:
        dic[key].append(value)
    else:
        dic[key] = [value]

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('cnf_file')
    args = parser.parse_args()
    variables, clauses = parse_input_walk_sat(args.cnf_file)
    t0 = time.time()
    var_to_clauses = {}
    model = {}
    for var in variables:
        value = True
        if random.random() < 0.5:
            value = False
        model[var] = value

    for c in clauses:
        for v in c:
            add_to_list_in_dict(var_to_clauses, int(math.fabs(v)), c)
    getBack = walkSAT(model,clauses,var_to_clauses,0.3)
    t1 = time.time()
    total = t1-t0
    file_list = args.cnf_file.split('/')
    f = file_list[-1]

    if getBack is False:
        getBack = "UNSAT"
    else:
        newGetBack = "SAT Solution: "
        for k, v in getBack.iteritems():
            newGetBack = newGetBack + str(k) + " " + str(v) + " "
        getBack = newGetBack[:-1]

    to_print = "Instance: {} Time: {:.2f} Result: {}".format(f, total, getBack)
    print to_print
