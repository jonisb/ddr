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

    def output(self, inpath, outpath):
        settings = ['--max-read-rate=102400', '--sparse', '--no-trim', '--max-read-errors=0', '--min-read-rate=1Mi', '--max-slow-reads=1']
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
                    result = regex.match(r"(Copying non-tried blocks\.\.\.) Pass (\d+) \((forwards)\)", line)
                    if result:
                        self.values['status'] = result.group()
                    else:
                        if line == "Interrupted by user":
                            self.values['status'] = line
                        elif line == "Finished":
                            self.values['status'] = line
                        elif line == "GNU ddrescue 1.25":
                            pass
                        elif line == "Press Ctrl-C to interrupt":
                            pass
                        else:
                            print('not:', repr(line))
            else:
                yield self.values['pct rescued']