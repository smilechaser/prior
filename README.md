# prior.py

---
***DIRE WARNING:***

	I've done my best to test this but at the end of the day this is experimental. Use at your own risk! And make backups first!

	Don't blame me if it eats your files. :)
---

This is a utility script for ordering/reordering folder contents in order to maintain a priority list of files/folders.

Assume a list of folders such as:

	01_some_file.txt
	02_another_file
	03_a_project_folder
	04_another_folder

Where the first two digits indicate the priority.

You can adjust the ordering of any of the items up/down in priority by specifying an action and the name of the file/folder to operate on.

## Requirements

* python3

## Supported Platforms

* Tested on CPython 3.4.1 (Home Brew) OS X 10.10
* Should work on compatible platforms

## Installation

Nothing. This is a stand-alone script so there are no dependency modules to install or setup.py installs to run.

## Usage

To get help:

	python3 prior.py --help

## Examples

For all examples, assume an intial listing that looks like so:

	01_some_file.txt
	02_another_file
	03_a_project_folder
	04_another_folder

### Example 1
Move the last file/folder to the top:

	python3 prior.py top 04_another_folder

Yields:

	01_another_folder
	02_some_file.txt
	03_another_file
	04_a_project_folder

### Example 2
Move the first file/folder to the bottom:

	python3 prior.py bottom 01_some_file.txt

Yields:

	01_another_file
	02_a_project_folder
	03_another_folder
	04_some_file.txt

### Example 3
Move a file/folder up in priority:

	python3 prior.py up 03_a_project_folder

Yields:

	01_some_file.txt
	02_a_project_folder
	03_another_file
	04_another_folder

### Example 4
Move a file/folder down in priority

	python3 prior.py down 02_another_file

Yields:

	01_some_file.txt
	02_a_project_folder
	03_another_file
	04_another_folder


