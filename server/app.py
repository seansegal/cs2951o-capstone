from flask import Flask, jsonify
import subprocess

app = Flask(__name__)


"""
    Health endpoint. Returns JSON {success: true} if the API is up and running.
"""
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'success': True})

"""
    Test endpoint which runs a Bash script and returns the output.
"""
@app.route('/test_run', methods=['GET'])
def test_run():
    # Change this to subprocess.run() if we agree on Python 3.6
    output = subprocess.check_output(['./test_run.sh'])
    return jsonify({'test_run_output': output.decode('utf-8')})

if __name__ == '__main__':
    app.run(debug=True)
