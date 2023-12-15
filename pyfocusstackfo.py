# pyfocusstackfo — Utility to reallocate photos taken for focus stacking into folders.
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

#  Path prompted to user when choose folder with jpgs
PATH_LIBRARY_DEFAULT = '/home/eva/git/pyfocusstackfo'

#  Name of the future root folder where stacks will be located
FOLDER_NAME_ROOT = 'fs'

#  Maximum time interval between stacked photos
MAXDELTA = timedelta(seconds=2)

#  Min quantity of file to create separate folder
MINSTACKLEN = 5

#  If stack larger than this, program will print warning message, but create stack
BIG_STRANGE_STACKLEN = 10

#  Datetime format used in cameras exif
TIMESTAMP_FORMAT_EXIF = '%Y:%m:%d %H:%M:%S'


def read_jpg(jpg_folder: str) -> Tuple[List[str], List[datetime]]:
    """
    Read names of jpg files in source folder and timestamps when they were taken.
    Args:
        jpg_folder: path to folder where jpg stored
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
        sys.exit()

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
        if len(stack) >= MINSTACKLEN:
            stacks.append(stack)
            stack_stat[len(stack)] = stack_stat.get(len(stack), 0) + 1
            if len(stack) > BIG_STRANGE_STACKLEN:
                print(
                    f'Strange long stack ({len(stack)}) elements. From {stack[0]} to {stack[-1]}'
                )
        return stacks, stack_stat

    stack, stacks, stack_stat = [], [], {}
    stack.append(dates[0])

    for i in range(1, len(dates) - 1):
        delta = dates[i] - dates[i - 1]
        if delta <= MAXDELTA:
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


def get_folders() -> str:
    """
    Ask user about path where files stored.
    Returns:
        path
    """
    if not os.path.isdir(PATH_LIBRARY_DEFAULT):
        print('DEFAULT LIBRARY PATH DO NOT EXIST!\n!!\n!!CHANGE IT IN LINE 24\n!!')
    path_library, folder_jpg = '', ' '
    first_try = True
    while not os.path.isdir(path_library):
        if first_try:
            path_library = input(
                f'Input library path or press Enter for default, {PATH_LIBRARY_DEFAULT}\n\
Input: '
            )
            first_try = False
        else:
            path_library = input('That is not existing path! Please try again:\n')
        if path_library == '':
            path_library = PATH_LIBRARY_DEFAULT
            print('Default choosed. Ok. ', end='')
    print(f'Library path: {path_library}')

    first_try = True

    while not os.path.isdir(os.path.join(path_library, folder_jpg)):
        if first_try:
            folder_jpg = input('\nInput folder name with jpg:\n')
            first_try = False
        else:
            folder_jpg = input('That is not existing folder. Please try again:\n')
        folder_jpg == '' if folder_jpg == '/' else folder_jpg  # pylint: disable=pointless-statement

    result = os.path.join(path_library, folder_jpg)
    print(f'Nice. Program will do stack in folder: {result}')
    return result


def main() -> None:
    """
    Start the process. Start.
    """
    print('START\n')
    jpg_folder = get_folders()
    names, dates = read_jpg(jpg_folder)
    stacks = get_stacks(names, dates)
    move_stacks(stacks, jpg_folder)
    print('\nFINISH')


main()
