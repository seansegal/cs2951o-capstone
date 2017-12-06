package solver.sat;

public class VariableAssignment implements Move<SATStateData> {

	private int variableId;
	private boolean assignment;

	public VariableAssignment(int variableId, boolean assignment) {
		this.variableId = variableId;
		this.assignment = assignment;
	}

	@Override
	public boolean execute(State<SATStateData> state) {
		assert (variableId > 0);
		state.getData().setVariable(variableId, assignment);
		return true;
	}

	@Override
	public boolean undo(State<SATStateData> state) {
		assert variableId > 0;
		state.getData().unassign(variableId, assignment);
		return false;
	}

	@Override
	public String toString() {
		return String.format("MOVE: Assign var [%d] to be %s", variableId, Boolean.toString(assignment));
	}
}
