from flask import Flask, jsonify, request, render_template
import subprocess
import random
from flask_cors import CORS, cross_origin
import json
import os

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
    Test endpoint which runs a Bash script and returns the output.
"""
@app.route('/v1/sat-solver/instance', methods=['POST'])
def sat_solver():
    print(request.method)
    if request.method == 'POST':
        body = json.loads(request.data.decode('utf-8'))
        if 'fileContents' in body:
            fileContents = body['fileContents']
            file_name = CONSTANTS['TMP_FILE_NAME'] + str(random.randint(0, 1000)) + '.cnf'
            with open('../solvers/sat-solver/solver1/input/' + file_name, 'w') as f:
                f.write(fileContents)
                f.flush()
                try:
                    output = subprocess.check_output(['./run.sh', 'input/' + file_name], cwd='../solvers/sat-solver/solver1/')
                    return jsonify({'results': output.decode('utf-8')})
                except Exception as e:
                    print(e)


        else:
            return 'Invalid JSON: Missing fileContents field'
        return jsonify({'success': True})

    return 'Invalid method.'
    # Change this to subprocess.run() if we agree on Python 3.6

@app.route('/website', methods=['GET'])
def hello(name=None):
    return render_template('index.html', name=name)


if __name__ == '__main__':
    app.run(debug=True, threaded=CONSTANTS['THREADED'])
