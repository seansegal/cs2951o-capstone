#!/bin/bash

########################################
############# CSCI 2951-O ##############
########################################
E_BADARGS=65
if [ $# -ne 1 ]
then
	echo "Usage: `basename $0` <input>"
	exit $E_BADARGS
fi

input=$1

# Update this file with instructions on how to run your code given an input
python src/walk_sat.py $input

# To run our Walksat Solver, uncomment:
#python src/dpll.py $input
