#!/bin/python
# 2018-09-26/DBV
# Script for returning hostnames
# https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
# Limitations:
# * It's not possible to use numbers ahead of the integer placeholder
#
# TODO:
# [ ] Normalize the file path were the given hostsnames are being written to.

import random
import string
import re
import unicodedata
import os
import os.path
import sys

from flask import Flask, jsonify
from flask import make_response
from flask import request
from flask import abort

# Environment settings overwrite the defaults
DATA_OUTPUTDIR = './' if 'HOSTGEN_DATADIR' not in os.environ else os.path.join(os.environ['HOSTGEN_DATADIR'], '', '')
HOSTNAME_DIGITS = 4 if 'HOSTGEN_DIGITS' not in os.environ else int(os.environ['HOSTGEN_DIGITS'])
HOSTNAME_START = 1 if 'HOSTGEN_START' not in os.environ else int(os.environ['HOSTGEN_START'])
HOSTNAME_PATTERN = 'host%i' if 'HOSTGEN_PATTERN' not in os.environ else os.environ['HOSTGEN_PATTERN']
HOSTNAME_RANDOM_LENGTH = 8 if 'HOSTGEN_RANDOM_LENGTH' not in os.environ else int(os.environ['HOSTGEN_RANDOM_LENGTH'])
LISTEN_IP = '0.0.0.0' if 'HOSTGEN_LISTENIP' not in os.environ else os.environ['HOSTGEN_LISTENIP']
LISTEN_PORT = 5000 if 'HOSTGEN_LISTENPORT' not in os.environ else int(os.environ['HOSTGEN_LISTENPORT'])

app = Flask(__name__)

# Generate a filename from a string
# normalized, lowercase and without whitespaces, please
def create_csv_filename(input_string):
    """Create a filename based on a given string."""
    valid_filename = re.sub(r'\%i', '_0', input_string) + '.csv'
#    input_string = unicodedata.normalize('NFKD', input_string).encode('ascii', 'ignore')
#    input_string = unicode(re.sub(r'[^\w\s-]', '', input_string).strip().lower())
#    filename = unicode(re.sub(r'[-\s]+', '-', input_string)) + '.csv'
    return str(valid_filename)


# Write the hostname to a file
def write_hostname_to_file(filename, input_string):
    """ Write a string to a given filename, append only."""
    file_object = open(filename, "a")
    file_object.write(input_string + '\n')
    file_object.close()

# Search for a string in a file.
# Return true if found, or false if not found
def find_string_in_file(filename, search_string):
    """ Check if a given file contains a string"""
    # If the file does not exist, the string canno be found, ergo false
    if not os.path.exists(filename):
        return False
    else:
        if search_string in open(filename).read():
            return True
        else:
            return False

# Search a file for the highest integer in a line
# and return the value
def get_max_value_from_file(filename):
    """Search a file for the highest integer value and return it"""
    values = []
    hostname_file = open(filename)
    for line in hostname_file:
        values.append(int(re.findall('\d+', line)[0]))
    hostname_file.close()
    return max(values)


@app.route('/hostgen/api/v1.0/generate', methods=['GET'])
def get_generate():
    """generate a hostname based on the default settings"""
    pattern = HOSTNAME_PATTERN
    hostname = pattern.replace('%i', str(HOSTNAME_START).zfill(HOSTNAME_DIGITS))
    filename_for_hostname = create_csv_filename(pattern)
    hostname_exists = find_string_in_file(DATA_OUTPUTDIR + filename_for_hostname, hostname)
    if hostname_exists is True:
        new_hostnumber = get_max_value_from_file(DATA_OUTPUTDIR + filename_for_hostname) + 1
        hostname = pattern.replace('%i', str(new_hostnumber).zfill(HOSTNAME_DIGITS))

    hostname = str(hostname)
    write_hostname_to_file(DATA_OUTPUTDIR + filename_for_hostname, hostname)
    return jsonify({'hostname': hostname})

# Generate a hostname with the API and POST settings
@app.route('/hostgen/api/v1.0/generate', methods=['POST'])
def post_generate():
    """Generate a uniq hostname"""
    if not request.json or not 'pattern' in request.json:
        abort(400)
    else:
        pattern = request.json.get('pattern')

    # Set the number of digits
    if 'digits' in request.json:
        digits = request.json.get('digits')
    else:
        digits = 4

    # Set the start decimal
    if 'start' in request.json:
        start_number = str(request.json.get('start')).zfill(digits)
    else:
        start_number = str(1).zfill(digits)

    # Build the initial hostname
    hostname = pattern.replace('%i', str(start_number))
    filename_for_hostname = create_csv_filename(pattern)
    hostname_exists = find_string_in_file(DATA_OUTPUTDIR + filename_for_hostname, hostname)
    if hostname_exists: # Find the highest one and add one. Replace the hostname pattern then.
        new_hostnumber = get_max_value_from_file(DATA_OUTPUTDIR + filename_for_hostname) + 1
        hostname = pattern.replace('%i', str(new_hostnumber).zfill(digits))

    hostname = str(hostname)
    write_hostname_to_file(DATA_OUTPUTDIR + filename_for_hostname, hostname)
    return jsonify({'hostname': hostname})


# Get a random hostname string
@app.route('/hostgen/api/v1.0/random', methods=['GET'])
def get_random():
    """ Return a completely random hostname"""
    random_hostname = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(HOSTNAME_RANDOM_LENGTH)).lower()
    write_hostname_to_file(DATA_OUTPUTDIR + 'hostname_random.csv', random_hostname)
    return jsonify({'hostname': random_hostname})

# Error handling
@app.errorhandler(404)
def not_found(error):
    """Handing 404 messages"""
    error_message = {
        'error': 'Not found.',
        'info': 'Try: http//:<host>:<port>/hostgen/api/v1.0/generate',
        'url': 'https://github.com/Spreadcat/hostgen'
    }
    return make_response(jsonify(error_message), 404)

if __name__ == '__main__':
    app.run(host=LISTEN_IP, port=LISTEN_PORT)
    app.run(debug=True)
