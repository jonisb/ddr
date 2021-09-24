from subprocess import Popen, PIPE
from pathlib import Path
import re as regex



class ddrescue_class:
    bin = Path('ddrescue')

    def __init__(self):
        self.get_version()
        self.values = {}

    def run_ddrescue(self, command):
        return Popen(command, stdout=PIPE, universal_newlines=True) # , bufsize=1

    def get_version(self):
        settings = ['--version']
        command = [
            self.bin,
            *settings,
            ]
        with self.run_ddrescue(command) as proc:
            while proc.poll() is None:
                line = proc.stdout.readline()
                result = regex.match(r"GNU ddrescue ([\d\.]+)\n", line)
                if result:
                    self.version = result.groups()[0]
                    return self.version
