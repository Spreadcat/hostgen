# hostgen
A small service to generate unique host names and make them accessible via REST API.
This python script will open a port on the local machine and wait for REST API calls. Depending on the call, it will return a unique host name each time and make sure it's not using the same host name again.

It can be configured to use a pattern or a random string.

----

# Running the script

In order to run the script, python is required and the module [flask](http://flask.pocoo.org/)

    $ mkdir ~/hostgen
    $ cd ~/hostgen
    $ virtualenv flask
    $ ./flask/bin/pip install flask
    $ ./flask/bin/pyhon ./hostgen.py

----

## Warning

This solution only serves on request at a time, since it's using the internal development server of flask.

A later version might switch over to a more production like setup.

----

## Default settings

The default settings are use in GET requests to the REST API. If you want to overwrite them in your request, use a PUSH request with the API call `generate` (see below).

*   **Data directory**

    This setting influences where the script stores its data about which hostname has been already created. Deleting/moving the data or changing the datadir will affect the hostname generation. An empty directory will reset the script and the generation will start from the beginning (as defined by `HOSTGEN_START`).

    Default: `./`

    Environment variable: `HOSTGEN_DATADIR`

    Example: `export HOSTGEN_DATADIR='./'`

    **Note**: The directory must exist.


*   **Number of digits**

    This setting influences how many digits the generate hostname will have. With the default setting, any hostname will be appended with four (4) digits: `example0001`

    Default: `4`

    Environment variable: `HOSTGEN_DIGITS`

    Example: `export HOSTGEN_DIGITS=4`


*   **Start digits**

    The start digits set the value from where the integer part of the host names is counting upwards.

    Default: `1`

    Environment variable: `HOSTGEN_START`

    Example: `export HOSTGEN_START=1`

    **Note:** Setting this vaule below a value that already has been used, will still result in the highest value being used for the increment, unless the specific host name matching the start value does not exist.

    Example: The hostnames `example0001, example0002, example0005, example0006` have already been returned. Setting the start value to `3`, will generate the hostname `example0003` (because it's not existing). The next hostname after that will be `example0007`, not `example0004`.

*   **Pattern**

    The pattern is used to generate a hostname with a specific layout and increasing integer. The placeholder for the integer is `%i`.

    Default: `host%i`

    Environment variable: `HOSTGEN_PATTERN`

    Example: `export HOSTGEN_PATTERN='host%i'

    **Note:** Avoid using integers in the pattern (like `host1%i`. This will lead to problems with the generation of names.


*   **Random pattern length**

    This value determins the string length of the hostname when using the random hostname call `random`.

    Default: `8`

    Environment variable: `HOSTGEN_RANDOM_LENGTH`

    Example: `export HOSTGEN_RANDOM_LENGTH=8`


*   **Listen IP**

    This setting sets the listen IP for the service. The IP must be in in the format of version 4 (`0.0.0.0`).

    The default settings is to listen on all interfaces.

    Default: `0.0.0.0`

    Environment variable: `HOSTGEN_LISTENIP`

    Example: `export HOSTGEN_LISTENIP='0.0.0.0'


*   **Listen Port**

    This setting influences on which port the service is listening for incoming calls.

    Default: `5000`

    Environment variable: `HOSTGEN_LISTENPORT`

    Example: `export HOSTGEN_LISTENPORT=5000`

----

##API
### Generate

*   **URL**:

    `/hostgen/api/v1.0/generate`

*   **Method**
    GET

*   **URL Params**
    None.

*   **Data Params**
    None.

*   **Success Response**
    200

       `{"hostname": "<string>:"}`

*   **Error Response**
    404

*   **Sample Call**

       ```
       $ curl http://example.com:5000/hostgen/api/v1.0/generate
       ```

*   **Notes**

    Unless specific environment variables have been set, the script will assume default values and return hostnames based on those values. See the section [Default settings](#Default settings) for more information.


### Generate
*   **URL**

    `hostgen/api/v1.0/generate

*   **Method**

    `POST`

*   **URL Params**

    None

*   **Data Params**

    *   **pattern**

        Defines the pattern to use for the generated host name. See [Default settings](#Default settings) for information about usage.

    *   **digits**

        Defines the number of digits to append to a generate host name. See [Default settings](#Default settings) for information about usage.

    *   **start**

        Defines the start value for the appended host integer. See [Default settings](#Default settings) for information about usage.

*   **Success Response**

    200

    `{"hostname": "<string>}`

*   **Error Response**

    404

    `{"error": "not found"}`

*   **Sample Call**

    The following call will use the POST method to specify parameter for the required hostname:

      *   The host name must match the pattern `host`, followed by a digit.
      *   The digit must have four numbers, missing numbers are filled up with zeros.
      *   The start digit is `1`.

    ```
    $ curl \
        -i \
        -H "Content-Type: application/json" \
        -X POST \
        -d '{"pattern":"host%i", "start": 1, "digits": 4}' \
        http://localhost:5000/hostgen/api/v1.0/generate
    ```

    For the first call against the api, the return will be:

        {"hostname":"host0001"}

    Any subsequent call will increase the digit by 1:

        {"hostname":"host0002"}
        {"hostname":"host0003"}
        {"hostname":"host0003"}
        ...


*   **Notes**

    The data type being sent to the method must(!) be `application/json`. Otherwise the call will be rejected.

----


# Docker

There a docker build file which will generate an image to run the script in a docker environment.

## Build

To build the docker image, just run the usual build command in the directory with the file `Dockerfile`.

        $ docker build --tag hostgen .


## Environment variables

All all internal environment variables are pre-defined in the docker build.

        HOSTGEN_DATADIR
        HOSTGEN_DIGITS
        HOSTGEN_LISTENIP
        HOSTGEN_LISTERNPORT
        HOSTGEN_PATTERN
        HOSTGEN_RANDOM_LENGTH
        HOSTGEN_START

They can be overwritten during the container startup using the parameter `-e`. Example:

        $ docker run -i -e HOSTGEN_DATADIR=/var/log/ ...

If not specified, the values will be set according to the docker file (not according to the script).


## Ports

The port `5000` is exposed per default. However, when changing the environment variable `HOSTGEN_LISTENPORT`, the changed port can be made accessible using the parameter `-p`. Example:

        # Exposes container port 5010 on localhost 5000.
        $ export HOSTGEN_LISTENPORT=5010
        $ docker run -i -p 5000:5010 ...


## Storage

Since the docker container will per default write the data stored in it's own non-persistent storage, any restart of the container will reset the host API.

Within the container the directory `/data/` is available to write the data to.

Mount some local storage, to keep the data files consistent.

        # Mount the data files in `/data/hostgen` and
        # redirect the files to `/data within the container.
        $ mkdir -p /data/hostgen
        $ docker -i -v /data/hostgen:/data -e HOSTGEN_DATADIR='/data' ...

----

# Author & Feedback

*   Daniel Buøy-Vehn
    daniel@micronerds.org

