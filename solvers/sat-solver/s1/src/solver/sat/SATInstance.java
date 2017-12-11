package solver.sat;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * A simple class to represent a SAT instance.
 */
public class SATInstance {
	// The number of variables
	int numVars;

	// The number of clauses
	int numClauses;

	// The set of variables (variables are strictly positive integers)
	Set<Integer> vars = new HashSet<Integer>();

	// The list of clauses
	List<Set<Integer>> clauses = new ArrayList<Set<Integer>>();

	Map<Integer, List<Integer>> varToClauses;

	public SATInstance(int numVars, int numClauses) {
		this.numVars = numVars;
		this.numClauses = numClauses;
		this.varToClauses = new HashMap<>();
	}

	void addVariable(Integer literal) {
		vars.add((literal < 0) ? -1 * literal : literal);
	}

	void addClause(Set<Integer> clause) {
		clauses.add(clause);
		for (int literal : clause) {
			if (!this.varToClauses.containsKey(literal)) {
				this.varToClauses.put(literal, new ArrayList<>());
			}
			this.varToClauses.get(literal).add(clauses.size() - 1);
		}
	}

	public Set<Integer> getVars() {
		return Collections.unmodifiableSet(this.vars);
	}

	public String toString() {
		StringBuffer buf = new StringBuffer();
		buf.append("Number of variables: " + numVars + "\n");
		buf.append("Number of clauses: " + numClauses + "\n");
		buf.append("Variables: " + vars.toString() + "\n");
		for (int c = 0; c < clauses.size(); c++)
			buf.append("Clause " + c + ": " + clauses.get(c).toString() + "\n");
		return buf.toString();
	}
}
