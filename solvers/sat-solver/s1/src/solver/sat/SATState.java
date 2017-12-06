package solver.sat;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

/**
 * A simple class to represent a SAT solution.
 */
public class SATState implements State<SATStateData> {

	private SATInstance instance;
	private Map<Integer, Boolean> varAssignment;
	private Set<Integer> unsatisfied;
	private boolean isConflict = false;

	public SATState(SATInstance instance) {
		this.varAssignment = new HashMap<>();
		this.instance = instance;
		this.unsatisfied = new HashSet<>();
		for (int i = 0; i < instance.clauses.size(); i++) {
			this.unsatisfied.add(i);
		}
	}

	public SATState(SATState satState) {
		SATStateData data = satState.getData();
		this.instance = data.getInstance();
		this.varAssignment = data.getVarAssignment();
		this.unsatisfied = data.getUnsatisfied();
	}

	public void conflictFound() {
		this.isConflict = true;
	}

	public boolean isConflict() {
		return isConflict;
	}

	public boolean isSolution() {
		if (unsatisfied.isEmpty()) {
			return true;
		}
		if (this.varAssignment.size() != this.instance.numVars) {
			return false;
		}
		return checkAssignment(this.varAssignment, this.instance.clauses);
	}

	private boolean checkAssignment(Map<Integer, Boolean> assignment, List<Set<Integer>> clauses) {
		// This should only be called with a complete assignment.
		assert (this.varAssignment.size() == this.instance.numVars);
		for (Set<Integer> clause : clauses) {
			boolean satisfied = false;
			for (int literal : clause) {
				if (((literal > 0 && varAssignment.get(literal))
						|| (literal < 0 && !varAssignment.get(-1 * literal)))) {
					satisfied = true;
					break;
				}
			}
			if (!satisfied) {
				return false;
			}
		}
		return true;
	}

	/* No longer used. */
	public SATState copy() {
		return new SATState(this);
	}

	@Override
	public List<Move<SATStateData>> getValidMoves() {
		// Naive: Return all possible assignments from here.
		List<Move<SATStateData>> moves = new ArrayList<>();
		VariableAssignment move = inference();
		if (move != null) {
			moves.add(move);
			return moves;
		}

		return getNextBranch();
	}

	@Override
	public SATStateData getData() {
		return new SATStateData(instance, varAssignment, unsatisfied, this);
	}

	@Override
	public void setData(SATStateData data) {
		this.instance = data.getInstance();
		this.unsatisfied = data.getUnsatisfied();
		this.varAssignment = data.getVarAssignment();

	}

	private VariableAssignment inference() {
		VariableAssignment move;
		move = unitPropogation();
		if (move != null) {
			return move;
		}
		move = pureLiteral();
		if (move != null) {
			return move;
		}
		return null;
	}

	/* Finds next branching point using Jerslow-Wang heuristic. */
	private List<Move<SATStateData>> getNextBranch() {
		int TO_CONSIDER = 1; // Number to choose from randomly.
		Map<Integer, Double> score = new HashMap<>();
		PriorityQueue<Integer> pq = new PriorityQueue<>(instance.vars.size(),
				(o1, o2) -> score.get(o2).compareTo(score.get(o1)));
		for (int var : this.instance.vars) {
			double varSum = 0.0;
			if (!varAssignment.containsKey(var)) {
				if (this.instance.varToClauses.containsKey(var)) {
					for (int clause : this.instance.varToClauses.get(var)) {
						if (this.unsatisfied.contains(clause)) {
							varSum += Math.pow(2, -1 * count(instance.clauses.get(clause)));
						}
					}
				}
				score.put(var, varSum);
				pq.add(var);
				varSum = 0.0;
				if (this.instance.varToClauses.containsKey(-1 * var)) {
					for (int clause : this.instance.varToClauses.get(-1 * var)) {
						// If the clause isn't satisfied
						if (this.unsatisfied.contains(clause)) {
							varSum += Math.pow(2, -1 * count(instance.clauses.get(clause)));
						}
					}
				}
				score.put(-1 * var, varSum);
				pq.add(-1 * var);

			}
		}
		if (pq.isEmpty()) {
			return new ArrayList<>();
		}
		List<Integer> potentialMoves = new ArrayList<>();
		int i = 0;
		while (!pq.isEmpty() && i < TO_CONSIDER) {
			i++;
			potentialMoves.add(pq.poll());
		}
		Collections.shuffle(potentialMoves);

		List<Move<SATStateData>> moves = new ArrayList<>();
		int literal = potentialMoves.get(0);
		moves.add(new VariableAssignment(Math.abs(literal), literal > 0));
		moves.add(new VariableAssignment(Math.abs(literal), literal <= 0));
		return moves;
	}

	private int count(Set<Integer> clause) {
		int c = 0;
		for (int literal : clause) {
			if (!varAssignment.containsKey(Math.abs(literal))) {
				c++;
			}
		}
		return c;
	}

	/* New version of Pure Literal Elimination */
	private VariableAssignment pureLiteral() {
		for (int var : instance.vars) {
			if (varAssignment.containsKey(var)) {
				continue;
			}
			int posCount = 0;
			int negCount = 0;
			if (instance.varToClauses.containsKey(var)) {

				for (int clause : instance.varToClauses.get(var)) {
					if (unsatisfied.contains(clause)) {
						posCount++;
					}
				}
			}
			if (instance.varToClauses.containsKey(-1 * var)) {
				for (int clause : instance.varToClauses.get(-1 * var)) {
					if (unsatisfied.contains(clause)) {
						negCount++;
					}
				}
			}
			if (negCount > 0 && posCount == 0) {
				return new VariableAssignment(var, false);
			} else if (negCount == 0 && posCount > 0) {
				return new VariableAssignment(var, true);
			}

		}

		return null;
	}

	/* Old version of Pure Literal Elimation, currently not called. */
	private VariableAssignment pureLiteralElimination() {
		for (int var : instance.vars) {
			int positive = 0;
			if (varAssignment.containsKey(var)) {
				continue;
			}
			for (int clause : unsatisfied) {
				Set<Integer> currentClause = instance.clauses.get(clause);
				if (currentClause.contains(var) && currentClause.contains(-1 * var)) {
					// Has both literals in one clause, no way to do pure literal elimination.
					positive = 0;
					break;
				}
				if (currentClause.contains(var)) {
					if (positive == -1) {
						// We've already seen a negated literal, so break.
						positive = 0;
						break;
					}
					positive = 1;
				} else if (currentClause.contains(-1 * var)) {
					if (positive == 1) {
						// We've already seen a positive literal, so break.
						positive = 0;
						break;
					}
					positive = -1;
				}
			}
			if (positive != 0) {
				return new VariableAssignment(var, positive == 1);
			}
		}
		return null;
	}

	/* Unit Propagation */
	private VariableAssignment unitPropogation() {
		for (int clause : unsatisfied) {
			int count = 0;
			int toRet = 0;
			for (int var : instance.clauses.get(clause)) {
				if (!varAssignment.containsKey(Math.abs(var))) {
					count++;
					toRet = var;
					if (count > 1) {
						break;
					}
				}
			}
			if (count == 1) {
				assert toRet != 0;
				return new VariableAssignment(Math.abs(toRet), toRet > 0);
			}

		}
		// No unit propagation.
		return null;
	}

}
