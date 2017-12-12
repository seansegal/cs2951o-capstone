from flask import Flask, jsonify, request, render_template
from multiprocessing import Process
import subprocess
import datetime
import hashlib
import random
from pathlib import Path
from flask_cors import CORS, cross_origin
import json
import os
import uuid

app = Flask(__name__)
workers = []

# TODO: Move to a config file (yaml?)
CONSTANTS = {
    'THREADED': True,
    'MAX_PROCESSES': 10,
    'TMP_FILE_NAME': 'tmp_file'
}

SOLVERS = {
    'dpll': 's1',
    'walk-sat': 's2',
}

DEFAULT_SOLVER = 'dpll'

def solve_instance(file_id, solver_path):
    file_name = file_id + '.cnf'
    with  open('../data/info/'+ file_id + '.json', 'r+') as f:
        info = json.load(f)
        info['status'] = 'running'
        f.seek(0)
        f.write(json.dumps(info))
        f.truncate()
        f.flush()
        try:
            output = subprocess.check_output(['./run.sh', 'input/' + file_name], cwd='../solvers/sat-solver/'+ solver_path +'/')
            info['status'] = 'solved'
            info['result'] = parse_last_line(output.decode('utf-8'))
        except Exception as e:
            info['status'] = 'error'
            info['errorMessage'] = str(e)
        finally:
            f.seek(0)
            f.write(json.dumps(info))
            f.truncate()
            f.flush()
            f.close()


@app.route('/v1/sat-solver/json/instance', methods=['POST'])
def _create_cnf_file_from_json():

    # Upload an instance to be solved asynchronously
    if request.method == 'POST':
        body = json.loads(request.data.decode('utf-8'))
        if body.get('fileFormat', '') != 'cnf':
            raise ValueError('Only supported DIMACS file type is CNF')
        cnf = ['p cnf ' + body['numVariables'] + ' ' + body['numClauses']]
        cnf += body['clauses']
        file_contents = '\n'.join(cnf)
        file_name = body.get('fileName', '')
        solver_name = body.get('solverName', DEFAULT_SOLVER)
        solver_path = SOLVERS[solver_name]
        file_id = hashlib.sha256((file_name + + solver_name + file_contents).encode('UTF-8')).hexdigest()
        info_file = open('../data/info/'+ file_id + '.json', 'w')
        original_file = open('../solvers/sat-solver/' + solver_path + '/input/'+ file_id + '.cnf','w')
        file_info =  {
            'file_name:': file_name,
            'pid' : 'N/A',
            'status': 'processing',
            'time_created': datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y"),
            'result': 'N/A',
            'solver': solver_name,
        }
        info_file.write(json.dumps(file_info))
        original_file.write(file_contents)
        info_file.flush()
        original_file.flush()
        info_file.close()
        original_file.close()

        # Start a worker process with this file.
        worker = Process(target=solve_instance, args=(file_id,solver_path))
        worker.start()
        workers.append(worker)
        return jsonify({'fileId': file_id})
    return jsonify({'error': 'Invalid method.'})

"""
    Health endpoint. Returns JSON {success: true} if the API is up and running.
"""
@app.route('/v1/health', methods=['GET', 'POST'])
def health():
    return jsonify({'success': True})

"""
    Solvers endpoint. Returns JSON listing the names of the solvers.
"""
@app.route('/v1/solvers', methods=['GET'])
def solvers():
    return jsonify({'success': True, 'names': ['dpll', 'walk-sat']})

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
            return jsonify({'error': 'Invalid JSON: Missing fileContents field'})
        return jsonify({'success': True})

    return jsonify({'error': 'Invalid method.'})

"""
    Endpoint to create a new SAT instance. Returns an id that can be used to get
    data on that instance including its feasibility and solution if/when it has
    been solved.
"""
@app.route('/v1/sat-solver/instance', methods=['GET', 'POST'])
def instance():
    # Get information on a created instance.
    if request.method == 'GET':
        file_id = request.args.get('fileId')
        try:
            with open('../data/info/'+ file_id + '.json', 'r') as f:
                return jsonify(json.loads(f.read()))
        except Exception as e:
            return jsonify({'error': 'fileId {} does not exist.'.format(file_id)})

    # Upload an instance to be solved asynchronously
    if request.method == 'POST':
        body = json.loads(request.data.decode('utf-8'))
        if 'fileContents' in body:
            file_name = body.get('fileName', '')
            solver_name = body.get('solverName', DEFAULT_SOLVER)
            fileContents = body['fileContents']
            solver_path = SOLVERS[solver_name]
            file_id = hashlib.sha256((file_name + fileContents).encode('UTF-8')).hexdigest()
            info_file = open('../data/info/'+ file_id + '.json', 'w')
            original_file = open('../solvers/sat-solver/' + solver_path + '/input/'+ file_id + '.cnf','w')
            file_info =  {
                'file_name:': file_name,
                'pid' : 'N/A',
                'status': 'processing',
                'time_created': datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y"),
                'result': 'N/A',
                'solver': solver_name,
            }
            info_file.write(json.dumps(file_info))
            original_file.write(fileContents)
            info_file.flush()
            original_file.flush()
            info_file.close()
            original_file.close()

            # Start a worker process with this file.
            worker = Process(target=solve_instance, args=(file_id,solver_path))
            worker.start()
            workers.append(worker)
            return jsonify({'fileId': file_id, 'solver': solver_name})
    return jsonify({'error': 'Invalid method.'})

def parse_last_line(last_line):
    line_chunks = last_line.split(': ')
    print(line_chunks)
    parsed_line = {}
    parsed_line['time'] = line_chunks[2][:-7]
    if line_chunks[3].startswith('UNSAT'):
        parsed_line['result'] = 'UNSAT'
    else:
        parsed_line['result'] = 'SAT'
        solution = line_chunks[3][4:-1].split(' ')
        var_assignments = {}
        for i in range(0, len(solution), 2):
            var_assignments[i] = True if solution[i+1] == 'true' else False
        parsed_line['solution'] = var_assignments
    return parsed_line

@app.route('/website', methods=['GET'])
def load_website(name=None):
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(debug=True, threaded=CONSTANTS['THREADED'])
