# Online SAT Solver

This project was created as a Capstone for Brown's Prescriptive Analytics course, taught by Professor Kadioglu and Ugur Cetintemel.
Contributors: Ansel Vahle, Valentin Perez and Sean Segal.

This project offers a free online web service for solving SAT instances. Users can use either the REST API or the web interface to upload
SAT instances (in CNF format) and a solver with attempt to solve the instances.

## Solvers

### Approaches
* DPLL
* WalkSAT

### Constraints
DPLL is a complete search while WalkSAT is incomplete. Therefore, WalkSAT should
only be used on satisfiable instances.

<!-- TODO: Real numbers here -->
DPLL has been run on instances with x variables and x constraints.
WalkSAT has been run on instances with x variables and x constraints. 

## API Documentation

### Endpoints
POST /sat-solver/solve
POST /sat-solver/instance
GET /sat-solver/instance
GET /solvers
POST /sat-solver/json/instance

## Web Interface
![picture of web interface](https://i.imgur.com/AhrrMCL.png)


## Important Documents
Status Document: https://docs.google.com/document/d/1iwjp_cvajgF5vbjZ7F5JsT6-0Ys5Kmd-07lRbdCvN60/

## Future Improvements
