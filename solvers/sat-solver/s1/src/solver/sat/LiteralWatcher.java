package solver.sat;

import java.util.Map;

public class LiteralWatcher {

	private Map<Integer, Tuple> watchedLiterals;

	public LiteralWatcher(SATInstance instance) {

	}

	private class Tuple {
		private final int left;
		private final int right;

		public Tuple(int left, int right) {
			this.left = left;
			this.right = right;
		}
	}
}
