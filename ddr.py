#!/usr/bin/env python3
import sys
from time import sleep
from datetime import timedelta
from pathlib import Path
from rich.progress import Progress, BarColumn, TimeElapsedColumn, FileSizeColumn, TotalFileSizeColumn, TransferSpeedColumn, ProgressColumn, Text
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
    master_task = progress.add_task("overall", total=filessize)

    ddrescue = ddrescuelib.ddrescue_class()
    with progress:
        for path, size in fileslist:
            progress.log(f"Starting job #{path}")
            #sleep(0.2)
            progress.reset(jobs_task, total=size, description=f"job [bold yellow]#{str(path)[-40:]}")
            progress.start_task(jobs_task)
            Path3 = (Path2 / path.relative_to(Path1))
            for data in ddrescue.output(path, Path3):
                expand_size = eval(ddrescue.values['rescued'].replace('MB', f'* {kB} ** 2').replace('kB', f'* {kB}').replace('B', ''))
                progress.update(jobs_task, completed=expand_size, refresh=True)

            progress.advance(master_task, size)
            progress.log(f"Job #{path} is complete")
