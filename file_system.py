# -*- coding: utf-8 -*-
"""Utilities for file handling.

@Author       :  Sean Howard
@CreationDate :  2020/04/13
@UpdateDate   :  2020/04/18

Purpose
-------
The purpose of this library is to provide simplified wrapper functions for
standard file handling operations. This library assumes that it was populated
using a a cookiecutter template. Anything with the cookiecutter syntax
should be replaced with keyed values with the project is initialized.

"""

import os
from shutil import copy2, move
from zipfile import ZipFile


def copy_file(origin, destination, keep=True):
    """Copy the file or archive from origin location to destination.

    Summary
    -------
    This function is used to copy a speficied file or archive from it's
    origin location to a destination folder.

    Requires
    --------
    os

    Parameters
    ----------
    origin : STRING
        The origin fully qualified path for the file to move.
    destination : STRING
        The destination folder for the file.
    keep : BOOLEAN
        Keep the file in the original location. The default value is True.

    Returns
    -------
    msg : STRING
        A message string describing results of the function. Any msg starting
        with "Error" means that the function didn't work properly

    """
    # just the name of the file for reporting
    file_name = origin.split("/")[-1]
    # check to make sure that file exists
    if os.path.exists(origin):
        # check to make sure that the desitination folder exists
        if os.path.exists(destination):
            new_loc = destination + "/" + origin.split("/")[-1]
            if os.path.exists(new_loc):
                msg = (f"Message: move_file file | {file_name} already exists"
                       " in destination")
            else:
                if keep:
                    copy2(origin, destination)
                else:
                    move(origin, destination)
                msg = (f"Message: move_file | successufully moved {file_name}"
                       f" to {destination}")
        else:
            msg = f"Error: move_file | {destination} does not exist"
    else:
        msg = f"Error: move_file | {origin} does not exist"
    return msg


def inspect_zip(z_archive):
    """Inspect the contents of a zip archive.

    Summary
    -------
    This function provides the list of files included in the zip file provided.

    Requires
    --------
    os
    zipfile

    Parameters
    ----------
    z_archive : STRING
        The full path to the zip archive.

    Returns
    -------
    file_list : LIST
        List of the files contained in the zip archive. Returns None if the
        the zip archive does not exist.
    msg : STRING
        A message string describing results of the function. Any msg starting
        with "Error" means that the function didn't work properly

    """
    # archive name for reporting
    arch_name = z_archive.split("/")[-1]
    # check to see if the zip file exists
    if os.path.exists(z_archive):
        # get the list of names in the file
        with ZipFile(z_archive) as inspect:
            content_list = inspect.infolist()
        msg = (f"Message: inspect_zip | {arch_name} was found and contents"
               " provided")
    # the file doesn't exists
    else:
        content_list = None
        msg = f"Error: inspect_zip | {arch_name} does not exists"
    return content_list, msg


def extract_files(z_archive, member=None):
    """Extract a file from a zip archive.

    Summary
    -------
    This function extracts 1 or more files from a zip archive. This function
    assumes that the zip archive is not password protected.

    Requires
    --------
    os
    zipfile

    Parameters
    ----------
    z_archive : STRING
        The full path to the zip archive.
    member : LIST
        This is a zipinfo object returned from the inspect zip function. The
        Member object can include 1 or more files in the archive. The default
        value is None which extracts all files from the archive.

    Returns
    -------
    msg : STRING
        A message string describing results of the function. Any msg starting
        with "Error" means that the function didn't work properly

    """
    # archive name for reporting
    arch_name = z_archive.split("/")[-1]
    # extract the files to the same folder as the archive
    path = "/".join(z_archive.split("/")[:-1])
    # check to make sure that the zip archive exists
    if os.path.exists(z_archive):
        try:
            if member is None:
                # extract all files
                with ZipFile(z_archive) as arch:
                    arch.extractall(path)
            else:
                # extract single file from the archive
                with ZipFile(z_archive) as arch:
                    arch.extract(member, path)
            msg = ("Message: extract_files | file(s) successfully extracted"
                   f" from {arch_name}")
        except ValueError:
            msg = ("Error: extract_file | there was a problem extracting"
                   f" the file(s) from {arch_name}")
    else:
        msg = (f"Error: extract_files | the zip archive {arch_name} does not"
               " exists")
    return msg
