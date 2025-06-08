## pyfocusstackfo — Utility to reallocate photos taken for focus stacking into folders.
# Copyright (C) 2023 Ilia Baidakov <baidakovil@gmail.com>
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <https://www.gnu.org/licenses/>.
"""This is the only file needed to run pyfocusstackfo. Check settings before using."""

import operator
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import piexif

#  Name of the future root folder where stacks will be located
FOLDER_NAME_ROOT = 'fs'

#  Maximum time interval between stacked photos
MAX_TIME_DELTA = timedelta(seconds=2)

#  Min quantity of file to create separate folder
MIN_STACK_LEN = 5

#  If stack larger than this, program will print warning message, but create stack
LENGTH_STACK_WARNING = 10

#  Datetime format used in cameras exif
TIMESTAMP_FORMAT_EXIF = '%Y:%m:%d %H:%M:%S'


def read_jpg(jpg_folder: str) -> Tuple[List[str], List[datetime]]:
    """
    Read names of jpg files in source folder and timestamps when they were taken.
    Args:
        jpg_folder: path to folder where jpgs are stored
    Returns:
        list of names & list of datetimes
    """
    print('\nRead jpg...', end='')
    names = [file for file in os.listdir(jpg_folder) if file.lower().endswith('.jpg')]
    names = sorted(names)

    if len(names) != 0:
        print(f'ok.\nGot {len(names)} JPG in folder')
    else:
        print('\nNo JPG files in folder! Exit')
        sys.exit(1)

    dates_bytes = [
        piexif.load(os.path.join(jpg_folder, name))['0th'][306] for name in names
    ]

    tsf = TIMESTAMP_FORMAT_EXIF
    dates = sorted([datetime.strptime(str(date)[2:-1], tsf) for date in dates_bytes])

    print(
        f'Got {len(dates)} timestamps in JPGs\nFROM: {dates[0]} \nTO  : {dates[-1]}\n'
    )

    return names, dates


def get_stacks(names: List[str], dates: List[datetime]) -> List[List[str]]:
    """
    Main function, creating list of stacks (list of lists) and print statistics on size
    of stacks.
    Args:
        names: list of photo names
        dates: list of dates from photos
    Returns:
        List of stacks
    """

    def done_stack(
        stacks: List[List[str]],
        stack_stat: Dict[int, int],
        stack: List[str],
    ) -> Tuple[List[List[str]], Dict[int, int]]:
        """
        Function to send new 'closed' jpg-filenames-list (stack) to list of stacks if
        needed, and refresh statistics on stack lenghts.
        Args:
            stacks: list of stacks
            stack_stat: dict with statistics on stack sizes
            stack: current ended ('closed') stack
        Returns:
            renewed list of stacks & renewed statistics
        """
        if len(stack) >= MIN_STACK_LEN:
            stacks.append(stack)
            stack_stat[len(stack)] = stack_stat.get(len(stack), 0) + 1
            if len(stack) > LENGTH_STACK_WARNING:
                print(
                    f'Strange long stack ({len(stack)}) elements. From {stack[0]} to {stack[-1]}'
                )
        return stacks, stack_stat

    stack = []
    stacks: List[List[str]] = []
    stack_stat: Dict[int, int] = {}
    stack.append(names[0])

    for i in range(1, len(dates)):
        delta = dates[i] - dates[i - 1]
        if delta <= MAX_TIME_DELTA:
            #  Dates near each other -> Add name to stack.
            stack.append(names[i])  # type: ignore
            if i == (len(dates) - 1):
                #  Finish cycle with adding stack to stacks.
                stacks, stack_stat = done_stack(stacks, stack_stat, stack)  # type: ignore
                del stack  # type: ignore
        else:
            # Dates far from each other -> Add stack to stacks
            stacks, stack_stat = done_stack(stacks, stack_stat, stack)  # type: ignore
            if i == (len(dates) - 1):
                # Finish cycle
                del stack  # type: ignore
            else:
                # Start new stack
                stack = [names[i]]
    #  Below just prettyprint
    for stacksize, stackcount in sorted(stack_stat.items(), key=operator.itemgetter(0)):
        spacer = ' ' if stacksize < 10 else ''
        print(f'Stack size {spacer}{stacksize} files: {stackcount} stacks')
    return stacks


def move_stacks(stacks: List[List[str]], jpg_folder: str) -> None:
    """
    Create 'fs' folder -> all the stack-folders inside of it -> move jpg-files-list
    (stacks) to their final folders
    Args:
        stacks: list of stacks
        JPGPATH: folder where located files in `stacks`
    """
    if not stacks:
        print('No stacks here! Exit')
        sys.exit(2)
    folder_count, file_count = 0, 0
    os.mkdir(os.path.join(jpg_folder, FOLDER_NAME_ROOT))
    print(f'\nRoot folder {FOLDER_NAME_ROOT} created')
    print('Start moving files...', end='')
    for stack in stacks:
        #  Prepare folder for moving files to
        stack_dirname = stack[0][:-4] + '_to_' + stack[-1][:-4]
        stack_path = os.path.join(jpg_folder, FOLDER_NAME_ROOT, stack_dirname)
        os.mkdir(stack_path)
        folder_count += 1
        #  Move files from origin to new folders
        for name in stack:
            src = os.path.join(jpg_folder, name)
            dst = os.path.join(stack_path, name)
            os.rename(src, dst)
            file_count += 1

    print(f'Ok:\n{folder_count} folders created\n{file_count} files moved')


def main(jpg_folder: str) -> None:
    """
    Start the process. Start!
    Args:
        jpg_folder: Path to folder with JPG files.
    """
    print('START\n')
    
    # Normalize the path to handle special characters and ensure it exists
    jpg_folder = os.path.abspath(os.path.expanduser(jpg_folder))
    
    if not os.path.exists(jpg_folder):
        print(f"Error: Path does not exist: {jpg_folder}")
        sys.exit(1)
    
    if not os.path.isdir(jpg_folder):
        print(f"Error: Path is not a directory: {jpg_folder}")
        sys.exit(1)
    
    names, dates = read_jpg(jpg_folder)
    stacks = get_stacks(names, dates)
    move_stacks(stacks, jpg_folder)
    print('\nFINISH')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python group_photos.py <jpg_folder_path>")
        print("Note: If path contains special characters like '!', wrap it in single quotes")
        print("Example: python group_photos.py '/path/with/special!chars'")
        sys.exit(1)
    main(sys.argv[1])
