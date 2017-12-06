package solver.sat;

public interface Move<T> {

	// Execute the move on the input state
	boolean execute(State<T> state);

	boolean undo(State<T> state);

}
