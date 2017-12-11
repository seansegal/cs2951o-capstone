package solver.sat;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class SATStateData {

	private final SATInstance instance;
	private final Map<Integer, Boolean> varAssignment;
	private final Set<Integer> unsatisfied;
	private final SATState state;

	public SATStateData(SATInstance instance, Map<Integer, Boolean> varAssignment, Set<Integer> unsatisfied,
			SATState state) {
		this.instance = instance;
		this.varAssignment = varAssignment;
		this.unsatisfied = unsatisfied;
		this.state = state;
	}

	public SATStateData(SATStateData data) {
		assert false; // Shouldn't be called.
		this.instance = data.instance;
		this.varAssignment = new HashMap<>();
		this.unsatisfied = new HashSet<>();
		this.state = data.state;
		for (Map.Entry<Integer, Boolean> entry : data.varAssignment.entrySet()) {
			this.varAssignment.put(entry.getKey(), entry.getValue());
		}
		for (int i : data.unsatisfied) {
			this.unsatisfied.add(i);
		}
	}

	public SATInstance getInstance() {
		return instance;
	}

	public Map<Integer, Boolean> getVarAssignment() {
		return varAssignment;
	}

	public void setVariable(int variableId, boolean assignment) {
		assert variableId > 0;
		assert !varAssignment.containsKey(variableId);
		varAssignment.put(variableId, assignment);

		int varIdFromLiteral = assignment ? variableId : -1 * variableId;
		List<Integer> toRemove = new ArrayList<>();

		for (int clause : this.instance.varToClauses.get(varIdFromLiteral)) {
			if (this.unsatisfied.contains(clause)) {
				toRemove.add(clause);
			}
		}
		for (int clause : toRemove) {
			this.unsatisfied.remove(clause);
		}

		// Check if there are any conflicts:
		if (instance.varToClauses.containsKey(-1 * varIdFromLiteral)) {
			for (int clause : instance.varToClauses.get(-1 * varIdFromLiteral)) {
				boolean conflictingClause = true;
				for (int literal : instance.clauses.get(clause)) {
					if (!varAssignment.containsKey(Math.abs(literal))
							|| varAssignment.get(Math.abs(literal)) == (literal > 0)) {
						conflictingClause = false;
						break;
					}
				}
				if (conflictingClause) {
					state.conflictFound();
				}
			}
		}
	}

	public void unassign(int variableId, boolean assignment) {
		assert variableId > 0;
		varAssignment.remove(variableId);
		int varLiteral = assignment ? variableId : -1 * variableId;
		// Clean up unsatisfied
		if (instance.varToClauses.containsKey(varLiteral)) {
			for (int clause : this.instance.varToClauses.get(varLiteral)) {
				boolean isUnsatisfied = true;
				for (int literal : instance.clauses.get(clause)) {
					if (varAssignment.containsKey(Math.abs(literal))
							&& (varAssignment.get(Math.abs(literal)) == (literal > 0))) {
						isUnsatisfied = false;
						break;
					}
				}
				if (isUnsatisfied) {
					unsatisfied.add(clause);
				}
			}
		}
	}

	public Set<Integer> getUnsatisfied() {
		return unsatisfied;
	}

	@Override
	public String toString() {
		String defaultVal = "true";
		StringBuilder builder = new StringBuilder();
		for (int var : this.instance.vars) {
			if (varAssignment.containsKey(var)) {
				builder.append(" " + var + " " + Boolean.toString(varAssignment.get(var)));
			} else {
				builder.append(" " + var + " " + defaultVal);
			}
		}
		return builder.substring(1).toString();
	}
}
