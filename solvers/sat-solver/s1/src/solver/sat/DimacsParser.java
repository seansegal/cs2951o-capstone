package solver.sat;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Scanner;
import java.util.Set;

/**
 * This class provides a static helper method that parses a given CNF file into
 * a simple SAT instance object.
 */
public class DimacsParser {
	public static SATInstance parseCNFFile(String fileName) throws Exception {
		SATInstance satInstance = null;

		try {
			Scanner read = new Scanner(new File(fileName));

			String line = null;
			String[] tokens = null;

			// comment lines start with "c", discard them
			while (read.hasNextLine()) {
				line = read.nextLine();
				tokens = line.split(" ");
				if (!tokens[0].equals("c"))
					break;
			}

			// this should be the problem line which starts with "p"
			if (!tokens[0].equals("p"))
				throw new IllegalArgumentException("Error: DIMACS file does not have problem line");

			if (!tokens[1].equals("cnf")) {
				System.out.println("Error: DIMACS file format is not cnf");
				return satInstance;
			}

			int numVars = Integer.parseInt(tokens[2]);
			int numClauses = Integer.parseInt(tokens[3]);
			satInstance = new SATInstance(numVars, numClauses);

			// parse clauses
			Set<Integer> clause = new HashSet<Integer>();
			while (read.hasNext()) {
				line = read.nextLine();
				tokens = line.split(" ");

				// skip comment lines
				if (tokens[0].equals("c"))
					continue;

				// clause line should end with 0
				if (!tokens[tokens.length - 1].equals("0"))
					throw new IllegalArgumentException(
							"Error: clause line does not end with 0 " + Arrays.toString(tokens));

				// create the clause
				for (int i = 0; i < tokens.length - 1; i++) {
					if (tokens[i].equals(""))
						continue;

					Integer literal = Integer.parseInt(tokens[i]);
					clause.add(literal);
					satInstance.addVariable(literal);
				}

				// add clause to instance
				satInstance.addClause(clause);
				clause = new HashSet<Integer>();
			}
		} catch (FileNotFoundException e) {
			throw new FileNotFoundException("Error: DIMACS file is not found " + fileName);
		}
		return satInstance;
	}
}