import math

def parse_input(cnf_file):
	with open(cnf_file) as f:
		problem = f.next().split(' ')
		while problem[0] != 'p':
			problem = f.next().split(' ')

		num_vars = int(problem[-2])
		num_clauses = int(problem[-1])
		variables = set()
		clauses = []
		for line in f:
			if line.isspace():
				break
			line = line.strip('\n').split(' ')
			current_clause = set()
			for literal in line:
				literal = int(literal)
				if literal == 0:
					break
				variables.add(int(math.fabs(literal)))
				current_clause.add(literal)
			clauses.append(current_clause)

		print "Number of variables: {}".format(num_vars)
		print "Number of clauses: {}".format(num_clauses)
		print "Variables: {}".format(list(variables))

		for idx, c in enumerate(clauses):
			print "Clause {}: {}".format(idx, list(c))

	return variables, clauses


def parse_input_walk_sat(cnf_file):
	with open(cnf_file) as f:
		problem = f.next().split(' ')
		while problem[0] != 'p':
			problem = f.next().split(' ')
		num_vars = int(problem[-2])
		num_clauses = int(problem[-1])
		variables = set()
		clauses = []
		for line in f:
			if line.isspace():
				break
			line = line.strip('\n').split(' ')
			current_clause = []
			for literal in line:
				literal = int(literal)
				if literal == 0:
					break
				variables.add(int(math.fabs(literal)))
				current_clause.append(literal)
			clauses.append(current_clause)

		print "Number of variables: {}".format(num_vars)
		print "Number of clauses: {}".format(num_clauses)
		print "Variables: {}".format(list(variables))

		for idx, c in enumerate(clauses):
			print "Clause {}: {}".format(idx, list(c))
	return variables, clauses
