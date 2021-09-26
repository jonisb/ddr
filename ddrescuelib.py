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

    def output(self, inpath, outpath, settings=()):
        #settings = ['--max-read-rate=102400', '--sparse', '--no-trim', '--max-read-errors=0', '--min-read-rate=1Mi', '--max-slow-reads=1']
        #settings = ['--sparse', '--no-trim', '--max-read-errors=0', '--min-read-rate=1Mi', '--max-slow-reads=1']
        command = [
            self.bin,
            *settings,
            inpath,
            outpath,
            outpath.with_suffix(outpath.suffix + '.log')
            ]
        with self.run_ddrescue(command) as proc:
            self.values['status'] = tuple()
            while proc.poll() is None:
                line = proc.stdout.readline().strip().replace('[A', '')
                if line == '':
                    continue
                result = regex.findall(r"\s*(\w[\w\s-]+):\s+(.*?)(?:,|$)", line)
                if result:
                    for res in result:
                        self.values[res[0]] = res[1].strip()
                        if 'time since last successful read' == res[0]:
                            yield self.values['pct rescued']
                else:
                    result = regex.match(r"(Copying non-tried blocks\.\.\.) Pass (\d+) \(((?:for|back)wards)\)", line)
                    if result:
                        self.values['status'] = result.group()
                    else:
                        if line == "Interrupted by user":
                            self.values['status'] = line
                        elif line == "Finished":
                            self.values['status'] = line
                        elif line == "Current status":
                            pass
                        elif line == "Initial status (read from mapfile)":
                            pass
                        elif line[:12] == "GNU ddrescue":
                            pass
                        elif line == "Press Ctrl-C to interrupt":
                            pass
                        elif line == "Too many read errors":
                            pass
                        elif line == "Too many slow reads":
                            pass
                        else:
                            print('not:', repr(line))
            else:
                yield self.values['pct rescued']


class ddrescuelog_class:
    bin = Path('ddrescuelog') # r'C:\Users\jonib\scoop\persist\cygwin\root\bin\ddrescuelog.exe'

    def run(self, command):
        return Popen(command, stdout=PIPE, universal_newlines=True)

    @property
    def version(self):
        try:
            return self._version
        except AttibuteError:
            settings = ['--version']
            command = [
                self.bin,
                *settings,
                ]
            with self.run(command) as proc:
                while proc.poll() is None:
                    line = proc.stdout.readline()
                    result = regex.match(r"GNU ddrescuelog ([\d\.]+)\n", line)
                    if result:
                        self._version = result.groups()[0]
                        return self._version
                        #return (self._version := result.groups()[0])

    def run_no_output(self, outpath, settings=()):
        command = [
            self.bin,
            *settings,
            outpath.with_suffix(outpath.suffix + '.log')
            ]
        with self.run(command) as proc:
            return proc.wait()
