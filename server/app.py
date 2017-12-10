from flask import Flask, jsonify, request, render_template
import subprocess
import random
from flask_cors import CORS, cross_origin
import json
import os
import uuid

app = Flask(__name__)

# TODO: Move to a config file (yaml?)
CONSTANTS = {
    'THREADED': True,
    'MAX_PROCESSES': 10,
    'TMP_FILE_NAME': 'tmp_file'
}

# TODO: move to an external file.
def _create_cnf_file_from_json(jsonCNF):
    dictCNF = json.loads(jsonCNF)
    if dictCNF['fileFormat'] != 'cnf':
        raise ValueError('Only supported DIMACS file type is CNF')
    cnf = ['p cnf ' + dictCNF['numVariables'] + ' ' + dictCNF['numClauses']]
    cnf += dictCNF['clauses']
    file_name = 'cnf_' + str(random.randint(0,999))
    cnf_file  = open( file_name, 'w')
    cnf_file.write('\n'.join(cnf))
    cnf_file.close()
    return


"""
    Health endpoint. Returns JSON {success: true} if the API is up and running.
"""
@app.route('/v1/health', methods=['GET', 'POST'])
def health():
    return jsonify({'success': True})


"""
    Endpoint which solves a SAT instance synchronously. In other words, this post
    request will hang until the solver returns or times out.
"""
@app.route('/v1/sat-solver/solve', methods=['POST'])
def solve_sat():
    if request.method == 'POST':
        body = json.loads(request.data.decode('utf-8'))
        if 'fileContents' in body:
            fileContents = body['fileContents']
            file_id = str(uuid.uuid4())
            file_name = CONSTANTS['TMP_FILE_NAME'] + file_id + '.cnf'
            with open('../solvers/sat-solver/s1/input/' + file_name, 'w') as f:
                f.write(fileContents)
                f.flush()
                try:
                    output = subprocess.check_output(['./run.sh', 'input/' + file_name], cwd='../solvers/sat-solver/s1/')
                    return jsonify({'results': output.decode('utf-8')})
                except Exception as e:
                    print(e)
        else:
            return 'Invalid JSON: Missing fileContents field'
        return jsonify({'success': True})

    return 'Invalid method.'

"""
    Endpoint to create a new SAT instance. Returns an id that can be used to get
    data on that instance including its feasibility and solution if/when it has
    been solved.
"""
@app.route('/v1/sat-solver/instance', methods=['POST'])
def create_new_instance():
    print(request.method)
    if request.method == 'POST':
        body = json.loads(request.data.decode('utf-8'))
        if 'fileContents' in body:
            file_id = str(uuid.uuid4())
            file_name = CONSTANTS['TMP_FILE_NAME'] + file_id + '.cnf'
            # TODO:  Add the element to a database + start running in a seperate thread.
    return 'Invalid method.'


@app.route('/website', methods=['GET'])
def load_website(name=None):
    return render_template('index.html', name=name)


def solve_instance(filename):



if __name__ == '__main__':
    app.run(debug=True, threaded=CONSTANTS['THREADED'])
