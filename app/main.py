import os, signal

def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)