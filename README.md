# Online SAT Solver

This project was created as a Capstone for Brown's Prescriptive Analytics course, taught by Professor Kadioglu and Ugur Cetintemel.
Contributors: Ansel Vahle, Valentin Perez and Sean Segal.

This project offers a free online web service for solving SAT instances. Users can use either the REST API or the web interface to upload
SAT instances (in CNF format) and a solver with attempt to solve the instances.

## Local Development

### Local setup
The server is written in Python 3.6 with Flask. To run the server, ensure that
you are running Python 3.6 by running `python --version` in a terminal. Next,
ensure that you have Flask installed.

Once you have all dependencies installed, you should be able to run the server.
Run `./run.sh` from your terminal. You should see a message saying that the server
has started.

Visit `localhost:5000/website` to see the website's homepage. You can also try
sending a GET request to `localhost:5000/v1/health` to ensure that the web server
is running.

### Adding a new solver
If you would like to give users access to a new solver, you will need to add a directory
for the new solver in `solvers/<solver-type>/<solver-name>`. Please ensure that the root of the directory has a `run.sh` script that has executable permissions. To add executable permissions, run `chmod u+x run.sh` from the root of the solver directory. Next, you should, open `server/app.py` and add the path to the solver to the SOLVER dictionary.  

Note that you can any type of solver as long as it expects exactly one file as input as
prints out a result in the CS2951O format as the last time. The parser for the solution
itself is expecting a SAT assignment so if this project is extended to add new solvers,
this code would likely need to changed.

### Code Overview

The `data` folder contains generated data files. There is no source code located in this folder.

The `server` folder contains all code for the server including the front-end web templates, which
are located in `server/templates`. The back-end code is located in the file `server/app.py`.

The `solvers` directory contains all available solvers. The directory structure for solvers should
follow the following hierarchical format: `solvers/<solver-type>/<solver-name>` where `<solver-type>`
is the type of problem that is solved (for example `sat-solver`).


## Solvers

### Approaches
SAT Solvers
* DPLL
* WalkSAT

### Constraints
DPLL is a complete search while WalkSAT is incomplete. Therefore, WalkSAT should
only be used on satisfiable instances.


## API Documentation

### Endpoints
* POST /sat-solver/solve: Solves a SAT instance synchronously.
* POST /sat-solver/instance: Starts a solver job. Returns a fileId used to check the status of the job.
* GET /sat-solver/instance?fileId=<fileId>: Returns information or the solution on a file that was uploaded.
* GET /solvers: Returns a list of all solvers.
* POST /sat-solver/json/instance: A JSON WEB API for solving a SAT instance. 

## Web Interface
![picture of web interface](https://i.imgur.com/AhrrMCL.png)


## Important Documents
Status Document: https://docs.google.com/document/d/1iwjp_cvajgF5vbjZ7F5JsT6-0Ys5Kmd-07lRbdCvN60/

## Possible Future Improvements
* Solution File Download
* Including more types of SAT solvers
* Including solvers for other types of problems
* User accounts (sign in, persistence of solve requests)
