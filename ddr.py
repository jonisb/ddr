#!/usr/bin/env python3
import sys
from time import sleep
from datetime import timedelta
from pathlib import Path
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn, FileSizeColumn, TotalFileSizeColumn, TransferSpeedColumn, ProgressColumn, Text
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
import ddrescuelib
__version__ = '0.0'


class TimeRemainingColumn2(ProgressColumn):
    """Renders estimated time remaining."""

    # Only refresh twice a second to prevent jitter
    max_refresh = 0.5

    def render(self, task: "Task") -> Text:
        """Show time remaining."""
        #remaining = task.time_remaining
        elapsed = task.elapsed
        #if remaining is None:
        if elapsed is None:
            return Text("-:--:--", style="progress.remaining")
        percentage = task.percentage
        #remaining_delta = timedelta(seconds=int(remaining))
        try:
            remaining_delta = timedelta(seconds=int((100.0/percentage)*int(elapsed))-int(elapsed))
        except ZeroDivisionError:
            return Text("-:--:--", style="progress.remaining")
        return Text(str(remaining_delta), style="progress.remaining")

"""
Scan source files
Check is destination has .log files
If no .log files run pass 1
else skip pass 1
"""
if __name__ == '__main__':
    kB = 1024
    Path1 = Path(sys.argv[1])
    Path2 = Path(sys.argv[2])

    fileslist = []
    filessize = 0
    for path in Path1.glob('**/*'):
        if path.is_dir():
            Path3 = (Path2 / path.relative_to(Path1))
            Path3.mkdir(exist_ok=True)
            continue

        fileslist.append((path, path.stat().st_size))
        filessize += path.stat().st_size
    #print(len(fileslist), filessize)
    progress = Progress("[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        TimeRemainingColumn2(),
        FileSizeColumn(),
        TotalFileSizeColumn(),
        TransferSpeedColumn(),
        auto_refresh=False)

    jobs_task = progress.add_task("jobs")
    master_task_size = progress.add_task("overall size", total=filessize)

    progress2 = Progress("[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        TimeRemainingColumn2(),
        auto_refresh=False)
    master_task_files = progress2.add_task("overall files", total=len(fileslist))

    ddrescue = ddrescuelib.ddrescue_class()
    ddrescuelog = ddrescuelib.ddrescuelog_class()
    #passes = [['--sparse', '--no-trim', '--max-read-errors=0', '--min-read-rate=1Mi', '--max-slow-reads=1'], ['--sparse', '--no-trim']]
    #passes = [('pass1', ddrescue.output, ('--sparse', '--no-trim', '--max-read-errors=0', '--min-read-rate=1Mi', '--max-slow-reads=1'), True), ('pass2', ddrescuelog.run_no_output, ('--done-status',), False), ('pass1', ddrescue.output, ('--sparse', '--no-trim'), True)]
    passes = [
        #('pass1', ddrescuelog.run_no_output, ('--delete-if-done',), False),
        #('pass2', ddrescue.output, ('--sparse', '--no-trim', '--max-read-errors=0', '--min-read-rate=1Mi', '--max-slow-reads=1'), True),
        #('pass3', ddrescuelog.run_no_output, ('--delete-if-done',), False),
        ('pass4', ddrescue.output, ('--sparse', '--verify-on-error', '--no-trim'), True),
        #('pass5', ddrescuelog.run_no_output, ('--delete-if-done',), False),
        ('pass6', ddrescue.output, ('--sparse', '--verify-on-error', '--no-scrape'), True),
        #('pass7', ddrescuelog.run_no_output, ('--delete-if-done',), False),
        ('pass8', ddrescue.output, ('--sparse', '--verify-on-error', '--idirect', '--retry-passes=5'), True)
        ]
    master_task_passes = progress2.add_task("overall passes", total=len(passes))

    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            progress, title="Jobs", border_style="green", padding=(1, 2)
        ),
        Panel.fit(progress2, title="overall", border_style="red", padding=(1, 2)),
        )

    with Live(progress_table, refresh_per_second=10):
        for Pass, func, settings, output in passes:
            for i, (path, size) in enumerate(fileslist.copy()):
                #progress.log(f"Starting job #{path}")
                #sleep(0.2)
                progress.reset(jobs_task, total=size, description=f"job [bold yellow]#{i+1}")
                progress.start_task(jobs_task)
                Path3 = (Path2 / path.relative_to(Path1))
                Pathlog = Path3.with_suffix(Path3.suffix + '.log')
                if Pathlog.exists():
                    if not ddrescuelog.run_no_output(Path3, ('--delete-if-done',)):
                        fileslist.remove((path, size))
                        filessize -= size

                    elif output:
                        for data in func(path, Path3, settings):
                            #sleep(0.2)
                            expand_size = eval(ddrescue.values['rescued'].replace('MB', f'* {kB} ** 2').replace('kB', f'* {kB}').replace('B', ''))
                            progress.update(jobs_task, completed=expand_size, refresh=True)
                    else:
                        if not func(Path3, settings):
                            fileslist.remove((path, size))
                else:
                    fileslist.remove((path, size))
                    filessize -= size

                progress.advance(master_task_size, size)
                progress2.advance(master_task_files, 1)
                #progress.log(f"Job #{path} is complete")
            progress.reset(master_task_size, total=filessize, description="overall size")
            progress2.reset(master_task_files, total=len(fileslist), description="overall files")
            progress2.advance(master_task_passes, 1)
