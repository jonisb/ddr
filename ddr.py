#!/usr/bin/env python3
import sys
from time import sleep
from pathlib import Path
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn,FileSizeColumn, TotalFileSizeColumn, TransferSpeedColumn
import ddrescuelib
__version__ = '0.0'

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
            progress.reset(jobs_task, total=size, description=f"job [bold yellow]#{path}")
            progress.start_task(jobs_task)
            Path3 = (Path2 / path.relative_to(Path1))
            for data in ddrescue.output(path, Path3):
                expand_size = eval(ddrescue.values['rescued'].replace('MB', f'* {kB} ** 2').replace('kB', f'* {kB}').replace('B', ''))
                progress.update(jobs_task, completed=expand_size, refresh=True)

            progress.advance(master_task, size)
            progress.log(f"Job #{path} is complete")
