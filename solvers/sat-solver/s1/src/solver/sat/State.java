package solver.sat;

import java.util.List;

public interface State<T> {

	List<Move<T>> getValidMoves();

	boolean isSolution();

	T getData();

	void setData(T data);

	State<T> copy();

	boolean isConflict();
}
