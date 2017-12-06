package solver.sat;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Usage example: read a given cnf instance file to create a simple sat instance
 * object and print out its parameter fields.
 */
public class Main {
	public static void main(String[] args) throws Exception {
		if (args.length == 0) {
			System.out.println("Usage: java Main <cnf file>");
			return;
		}

		String input = args[0];
		Path path = Paths.get(input);
		String filename = path.getFileName().toString();

		Timer watch = new Timer();
		watch.start();

		SATInstance instance = DimacsParser.parseCNFFile(input);
		// System.out.println(instance);

		SATState initialState = new SATState(instance);
		SearchPath<SATStateData> result = SearchRecursive.search(initialState, initialState); // TODO: get return value
																								// and have it
		// print
		// nicely to result
		watch.stop();
		System.out.println("Instance: " + filename + " Time: " + String.format("%.2f", watch.getTime()) + " Result: "
				+ resultToString(result));
	}

	private static String resultToString(SearchPath<SATStateData> result) {
		return (result.isSuccess() ? "SAT " + result.getFinal().getData().toString() : "UNSAT ");
	}
}
