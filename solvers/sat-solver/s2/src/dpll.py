import argparse
from parser import parse_input
import copy
import math
import operator
import time
import random
import pdb
import sys

beginning_clauses = []

def dpll(variables, unknown_clauses_indexes, model, sorted_var_counts, literal_to_clauses, clause_to_unassigned, last_P, last_sign):
    # print "variables: {0}".format(len(variables))
    # print "model: {0}".format(model)
    # print "clauses: {0}".format(clauses_indexes_to_clauses(unknown_clauses_indexes))

    if last_P is not None:
        status, new_unknown_classes_indexes, new_literal_to_clauses = status_unknown(model, unknown_clauses_indexes, literal_to_clauses, last_P, last_sign)
        if status is False:
            return False
        if status is True:
            return model
    else:
        new_unknown_classes_indexes = unknown_clauses_indexes
        new_literal_to_clauses = literal_to_clauses

    P, sign = find_unit_clause(new_unknown_classes_indexes, model)
    if P:
        return dpll(variables, new_unknown_classes_indexes.copy(), extend_model(model, P, sign), remove_var_from_var_counts(P, sorted_var_counts), new_literal_to_clauses, clause_to_unassigned, P, sign)

    # P, sign = find_pure_symbol(new_unknown_classes_indexes, variables, literal_to_clauses)
    # if P:
    #     #print "found pure symbol {0}".format(P)
    #     #variables_u, clauses_u, model_u, sorted_var_counts_u  = update_pure_symbol(P, sign, variables, clauses, model, sorted_var_counts)
    #     return dpll(variables, new_unknown_classes_indexes.copy(), extend_model(model, P, sign), remove_var_from_var_counts(P, sorted_var_counts), literal_to_clauses, clause_to_unassigned, P, sign)

    new_sorted_var_counts = copy.deepcopy(sorted_var_counts)
    whole_p = new_sorted_var_counts.pop()
    P = whole_p[0]
    sign = get_most_seen_sign(whole_p)

    got_back = dpll(variables, new_unknown_classes_indexes, extend_model(model, P, sign), new_sorted_var_counts, new_literal_to_clauses, clause_to_unassigned, P, sign)
    if got_back is False:
        got_back2 = dpll(variables, new_unknown_classes_indexes, extend_model(model, P, not sign), new_sorted_var_counts, new_literal_to_clauses, clause_to_unassigned, P, not sign)
        if got_back2 is False:
            return False
        else:
            return got_back2
    else:
        return got_back

def clauses_indexes_to_clauses(indexes):
    clauses = []
    for index in indexes:
        clauses.append(beginning_clauses[index])
    return clauses

# Some other DPLL structure with BCP attempting watched literals.
def dpll2(variables, clauses, model, sorted_var_counts, literal_to_clauses, clause_to_unassigned, last_P, last_sign):
    P, sign, new_literal_to_clauses, unknown_clauses, new_model, new_variables = bcp(model, clauses, variables, literal_to_clauses, last_P, last_sign)
    if P is False:
        return False
    if P is None:
        # choose new P.
        P = new_variables.pop()
        new_variables.add(P)
        sign = True
        return dpll2(remove_var(P, new_variables), unknown_clauses, extend_model(new_model, P, sign), sorted_var_counts, new_literal_to_clauses, clause_to_unassigned, P, sign)
    else:
        # found P, so propagate
        all_valid, unknown_clauses = all_clauses_valid(unknown_clauses, extend_model(new_model, P, sign), new_literal_to_clauses, P, sign)
        if all_valid is True:
            return new_model
        elif all_valid is False:
            return False
        else:
            return dpll2(new_variables, unknown_clauses, extend_model(new_model, P, sign), sorted_var_counts, new_literal_to_clauses, clause_to_unassigned, P, sign)

# Used to check whether a model is actually true with all the clauses from the beginning.
def all_beg_clauses_valid(model, literal_to_clauses, last_P, sign):
    is_unknown = False
    clauses_true_in_model = 0
    unknown_clauses = []
    for c in beginning_clauses:
        c_value = clause_value(c, model)
        if c_value is True:
            clauses_true_in_model += 1
        if c_value is False:
            return False, unknown_clauses
        if c_value is None:
            unknown_clauses.append(c)

    if clauses_true_in_model == len(clauses_indexes):
        return True, unknown_clauses

    return None, unknown_clauses

def all_clauses_valid(clauses_indexes, model, literal_to_clauses, last_P, sign):
    is_unknown = False
    clauses_true_in_model = 0
    unknown_clauses = set()
    for c_i in clauses_indexes:
        c = beginning_clauses[c_i]
        c_value = clause_value(c, model)
        if c_value is True:
            clauses_true_in_model += 1
        if c_value is False:
            return False, unknown_clauses
        if c_value is None:
            unknown_clauses.add(c_i)

    if clauses_true_in_model == len(clauses_indexes):
        return True, unknown_clauses

    return None, unknown_clauses

# Uses idea from Watched Literals by only traversing through clauses related to the last assignment
# and reduces the unknown_clauses as we find they're satisfied.
# Also returns a status of whether clauses are UNSAT or all clauses are True or there is still work to do (None)
def status_unknown(model, unknown_clauses_indexes, literal_to_clauses, last_P, last_sign):
    clauses_true_in_model = 0

    if last_sign:
        if -last_P not in literal_to_clauses:
            print "skipping"
            return None, unknown_clauses_indexes, literal_to_clauses

        a = -last_P
        potentials = literal_to_clauses[a]
    else:
        if last_P not in literal_to_clauses:
            print "skipping"
            return None, unknown_clauses_indexes, literal_to_clauses

        a = last_P
        potentials = literal_to_clauses[a]

    new_unknown_clauses_indexes = unknown_clauses_indexes.copy()
    new_literal_to_clauses = literal_to_clauses.copy()

    for c_i in potentials:
        if c_i not in new_unknown_clauses_indexes:
            continue

        c = beginning_clauses[c_i]
        c_value = clause_value(c, model)
        if c_value is True:
            new_unknown_clauses_indexes.remove(c_i)
            clauses_true_in_model += 1

        if c_value is False:
            return False, new_unknown_clauses_indexes, new_literal_to_clauses

        unassigned, assigned, numtrue = get_unassigned_assigned_numtrue(c, model)
        if numtrue > 0:
            # this means the clause is already satisfied so remove it.
            if c_i in new_unknown_clauses_indexes:
                new_unknown_clauses_indexes.remove(c_i)
                clauses_true_in_model += 1

        if numtrue == 0 and len(unassigned) == 1:
            new_unknown_clauses_indexes.remove(c_i)
            unit_var = unassigned[0]
            if unit_var > 0:
                model = extend_model(model, unit_var, True)
            else:
                model = extend_model(model, unit_var, False)
        elif len(unassigned) > 0:
            some_unassigned = unassigned[0]
            add_to_list_in_dict(new_literal_to_clauses, some_unassigned, c_i)
            new_literal_to_clauses[a].remove(c_i)

    if clauses_true_in_model == len(unknown_clauses_indexes):
        return True, new_unknown_clauses_indexes, new_literal_to_clauses

    return None, new_unknown_clauses_indexes, new_literal_to_clauses


# Attempt of Boolean Constraint Propagation with Watched Literals
def bcp(model, clauses, variables, literal_to_clauses, last_P, last_sign):
    if last_sign:
        if -last_P not in literal_to_clauses:
            print "lit skipping"
            return None, None, literal_to_clauses, clauses, model, variables

        a = -last_P
        new_literal_to_clauses = literal_to_clauses.copy()
        to_update = new_literal_to_clauses[-last_P]
    else:
        if last_P not in literal_to_clauses:
            print "first here"
            return None, None, literal_to_clauses, clauses, model, variables

        a = -last_P
        new_literal_to_clauses = literal_to_clauses.copy()
        to_update = new_literal_to_clauses[last_P]

    assigned_some_P = False
    new_model = model
    new_variables = variables
    unknown_clauses = clauses
    some_clause_update = False
    for c in to_update:
        unassigned, assigned, numtrue = get_unassigned_assigned_numtrue(c, model)
        if numtrue == 0 and len(unassigned) == 1:
            # make it satisfy the clause
            if not some_clause_update:
                unknown_clauses = copy.deepcopy(clauses)
                some_clause_update = True

            unknown_clauses.remove(c)
            P = unassigned[0]
            if P > 0:
                new_model = extend_model(model, P, True)
                new_variables = remove_var(P, new_variables)
                assigned_some_P = True
            else:
                new_model = extend_model(model, -P, False)
                new_variables = remove_var(-P, new_variables)
                assigned_some_P = True

        if numtrue == 0 and len(unassigned) == 0:
            return False, None, new_literal_to_clauses, unknown_clauses, new_model, new_variables

        if numtrue > 0:
            if not some_clause_update:
                unknown_clauses = copy.deepcopy(clauses)
                some_clause_update = True

            unknown_clauses.remove(c)
            continue

        one_unassigned = unassigned[0]
        add_to_list_in_dict(new_literal_to_clauses, one_unassigned, c)
        if a in new_literal_to_clauses and c in new_literal_to_clauses[a]:
            new_literal_to_clauses[a].remove(c)

    return None, None, new_literal_to_clauses, unknown_clauses, new_model, new_variables

def extend_model(model, P, sign):
    model_copy = model.copy()
    model_copy[P] = sign
    return model_copy

def remove_var(P, variables):
    new_vars = variables.copy()
    new_vars.remove(P)
    return new_vars

def find_pure_symbol(clauses_indexes, variables, literal_to_clauses):
    #new_clauses_indexes = clauses_indexes.copy()
    for var_to_check in variables:
        found_postive = False
        found_negative = False
        for c_i in clauses_indexes:
            if not found_postive and var_to_check in beginning_clauses[c_i]:
                found_postive = True
            if not found_negative and -var_to_check in beginning_clauses[c_i]:
                found_negative = True
            if found_negative and found_postive:
                break # we know that this variable is not a pure symbol so go to next.
        if found_postive != found_negative: #if we only find it as one sign
            clauses_having = literal_to_clauses[var_to_check]
            clauses_indexes = clauses_indexes - set(clauses_having)
            return var_to_check, found_postive
    return None, None

def split_var_and_sign(literal):
    if literal > 0:
        return literal, True
    return -literal, False

def get_unassigned_assigned_numtrue(clause, model):
    unassigned = []
    assigned = []
    numtrue = 0
    for v in clause:
        if v not in model and -v not in model:
            unassigned.append(v)
        else:
            assigned.append(v)
            if literal_true_in_model(v, model):
                numtrue += 1

    return unassigned, assigned, numtrue

def find_unit_clause(clauses_indexes, model):
    new_clauses_indexes = clauses_indexes.copy()
    for c_i in new_clauses_indexes:
        c = beginning_clauses[c_i]
        if len(c) == 1:
            unit_var = list(c)[0]
            return split_var_and_sign(unit_var)

        unassigned, assigned, numtrue = get_unassigned_assigned_numtrue(c, model)
        if numtrue > 0:
            # this means the clause is already satisfied so remove it.
            clauses_indexes.remove(c_i)
            continue

        if numtrue == 0 and len(unassigned) == 1:
            unit_var = unassigned[0]
            return split_var_and_sign(unit_var)

    return None, None

def remove_var_from_var_counts(var, var_counts):
    new_var_counts = copy.deepcopy(var_counts)
    for tup in new_var_counts:
        if tup[0] == var:
            new_var_counts.remove(tup)
            return new_var_counts
    return new_var_counts

def literal_true_in_model(l, model):
    if l > 0 and model[l] or l < 0 and not model[-l]:
        return True
    return False

def var_true_in_clause2(var, model):
    if (math.fabs(var) == float(var) and model[int(math.fabs(var))]) or \
        (math.fabs(var) != float(var) and not model[int(math.fabs(var))]):
        return True

    return False

def clause_value(clause, model):
    for literal in clause:
        v = int(math.fabs(literal))
        if v in model and literal_true_in_model(literal, model):
            return True

        if v not in model:
            return None

    if len(clause) == 0:
        print "got here because of empty clause"
    return False

def all_clauses_valid_old(clauses, model, last_P, sign):
    is_unknown = False
    if len(clauses) == 0:
        return True
    for c in clauses:
        if last_P not in c and -last_P not in c:
            is_unknown = True
            continue

        c_valid = is_clause_valid(c, model)
        if c_valid is None:
            is_unknown = True
        if c_valid is False:
            return False
    if is_unknown:
        return None
    return True

def is_clause_valid(clause, model):
    all_vars_count = len(clause)
    if all_vars_count == 0:
        return False

    vars_accounted = 0
    for var in clause:
        if int(math.fabs(var)) in model:
            vars_accounted += 1
            if var_true_in_clause(var, model):
                return True

    if vars_accounted == all_vars_count:
        return False

    return None

def add_to_list_in_dict(dic, key, value):
    if key in dic:
        dic[key].append(value)
    else:
        dic[key] = [value]

def get_literal_to_clauses(clauses):
    literal_to_clauses = {}
    for idx, c in enumerate(clauses):
        for l in c:
            # l1 = c.pop()
            # l2 = c.pop()
            # c.add(l1)
            # c.add(l2)
            #add_to_list_in_dict(literal_to_clauses, int(math.abs(l1)), idx)
            add_to_list_in_dict(literal_to_clauses, int(math.fabs(l)), idx)

    return literal_to_clauses

def get_clause_number_of_unassigned(clauses):
    num_clauses = len(clauses)
    clause_to_unassigned = {}
    for i in range(num_clauses):
        clause_to_unassigned[i] = len(clauses[i])

    return clause_to_unassigned

def get_var_counts(clauses):
    var_counts = {}
    for c in clauses:
        for v in c:
            if int(math.fabs(v)) not in var_counts:
                if v > 0:
                    var_counts[int(math.fabs(v))] = (1, 1) # First is how many times it appears as both positive and negative. Second is how many times it appears as positive.
                else:
                    var_counts[int(math.fabs(v))] = (1, 0)
            else:
                tup = var_counts[int(math.fabs(v))]
                if v > 0:
                    tup = (tup[0] + 1, tup[0] + 1)
                else:
                    tup = (tup[0] + 1, tup[0]) # Don't add to appearing since the value is negative.
                var_counts[int(math.fabs(v))] = tup

    sorted_var_counts = sorted(var_counts.items(), key=lambda x: x[1][0]) # sort by largest combined sum
    return sorted_var_counts

def get_most_seen_sign(whole_p):
    tup = whole_p[1]
    positive = tup[1]
    negative = tup[0] - positive
    return positive > negative

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cnf_file')
    args = parser.parse_args()
    variables, clauses = parse_input(args.cnf_file)
    t0 = time.time()
    sorted_var_counts = get_var_counts(clauses)
    literal_to_clauses = get_literal_to_clauses(clauses)
    clause_to_unassigned = get_clause_number_of_unassigned(clauses)

    beginning_clauses = clauses
    unknown_clauses_indexes = set(range(len(beginning_clauses)))
    P = variables.pop()
    variables.add(P)
    sign = True
    # set limit to 2000 since all these cnfs have at most ~1700 variables.
    sys.setrecursionlimit(2000)
    getBack = dpll(variables, unknown_clauses_indexes, {}, sorted_var_counts, literal_to_clauses, clause_to_unassigned, None, None)

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
