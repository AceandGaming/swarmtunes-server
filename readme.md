The server side code that runs Swarmtunes.

Tested to work on Ubuntu server.
It is recommended to use something like nginx for rate limiting and routing.

WARNING: Running run.sh or the python file without environment varibles will cause the server to auto download every song covered! This is arround 4-8GB of data for which the server will NOT be active while downloading.

*Note: a google drive api key is **required** and some python packages. HTTPS is also required due to user accounts*
