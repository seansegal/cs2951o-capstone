package solver.sat;

import java.util.ArrayList;
import java.util.List;

public class SearchPath<T> {

	private final List<Move<T>> moves;
	private final State<T> initialState;
	private State<T> finalState; // TODO: set?
	private boolean success;

	public SearchPath(State<T> initial, State<T> finalState, boolean success) {
		this.moves = new ArrayList<>();
		this.initialState = initial;
		this.finalState = finalState;
		this.success = success;
	}

	// Get the valid moves for the current SearchPath
	public List<Move<T>> getMoves() {
		return this.moves;
	}

	// Getter method to determine if this state is a success
	public boolean isSuccess() {
		return this.success;
	}

	// Get the initial state of the SearchPath
	public State<T> getInitial() {
		return this.initialState;
	}

	// Get the final state of the SearchPath
	public State<T> getFinal() {
		return this.finalState;
	}

	// Set the final state of the SearchPath
	public boolean setFinal(State<T> state) {
		// TODO
		this.finalState = state;
		return false;
	}
}
