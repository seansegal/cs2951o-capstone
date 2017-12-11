package solver.sat;

public class SearchRecursive {

	public static <T> SearchPath<T> search(State<T> initial, State<T> state) {

		if (state.isSolution()) {
			return new SearchPath<T>(initial, state, true);
		}

		// If we've already reached a conflict, stop.
		if (state.isConflict()) {
			return new SearchPath<T>(initial, state, false);
		}

		for (Move<T> move : state.getValidMoves()) {

			State<T> successor = state.copy();

			if (!move.execute(successor)) {
				continue;
			}

			SearchPath<T> result = search(initial, successor);
			if (result.isSuccess()) {
				return result;
			}

			// Backtracking (undo the move)
			move.undo(successor);
		}

		return new SearchPath<T>(initial, null, false);
	}

}
