#!/usr/bin/env python3

'''
Script for reordering files/folders of the format nn_name where:

    nn: a two digit number
    name: any arbitrary file/folder name

Useful for keeping a prioritized list of files/folders.
'''

import os
import re
import enum
import argparse

FILENAME_FILTER = re.compile(r'^(\d+)(_.*)')


class RecordNotFoundException(Exception):
    '''Raised if a Record matching the criteria provided cannot be found.'''
    pass


class Action(enum.Enum):
    '''Class of actions that can be performed on an item.'''

    up = 1
    down = 2

    first = 4
    last = 5
    top = 6
    bottom = 7

    @classmethod
    def parse(clz, str):

        try:
            return clz._keymap[str]
        except KeyError:
            raise KeyError('"{}" is not a valid '
                           '{} choice.'.format(str, clz.__name__))

Action._keymap = {n.name: n for n in Action}


class Record:
    '''Represents a file/folder of the form nn_name.'''

    def __init__(self, number, name):

        self.number = int(number)
        self.name = name

    @property
    def fullname(self):

        return '{:02d}{:s}'.format(self.number, self.name)

    def new_name(self, number):

        return '{:02d}{:s}'.format(number, self.name)


class Rename:
    '''Generic renamer that when executed renames the file/folder
    self.source as self.target.'''

    @property
    def conflict(self):
        return os.path.exists(self.target)

    def execute(self):
        os.rename(self.source, self.target)

    def __str__(self):
        return '{} old="{}" new="{}"'.format(self.__class__.__name__,
                                             self.source,
                                             self.target)


class FileRename(Rename):
    '''Rename operation for old file -> new file.'''

    def __init__(self, old_name, new_name):

        self.old_name = old_name
        self.new_name = new_name

    @property
    def target(self):
        return self.new_name

    @property
    def source(self):
        return self.old_name


class RecordRename(Rename):
    '''Rename operation for record -> record w/ new index.'''

    def __init__(self, record, new_index):

        self.record = record
        self.new_index = new_index

    @property
    def target(self):
        return self.record.new_name(self.new_index)

    @property
    def source(self):
        return self.record.fullname


class Ledger:
    '''Encapsulates our list of files and the operations we can
    perform on them.'''

    def __init__(self):

        self.records = []

        self._gather_files(self._get_filenames)

    def _get_filenames(self):

        return os.listdir('.')

    def _gather_files(self, data_provider):
        '''@param data_provider callable that returns an iterable'''

        self.records = []

        for file in data_provider():

            match = FILENAME_FILTER.match(file)

            if match:

                number, name = match.groups()

                self.records.append(Record(number, name))

        # i think os.listdir sorts anyways, but just to be safe...
        self.records.sort(key=lambda x: x.number)

    def get_record_by_name(self, name):
        '''Searches for the record whose fullname matches the
        specified name.'''

        for record in self.records:

            if record.fullname == name:
                return record

        raise RecordNotFoundException('Record "{}" not found.'.format(name))

    def commit(self):
        '''Perform file/folder renames according to the order of our
        records.'''

        # we only use a two-digit numbering prefix...
        assert(len(self.records) < 99)

        rename_list = self._generate_rename_list(self.records)

        self._process_rename_list(rename_list)

    @classmethod
    def _generate_rename_list(clz, records):
        '''Given a list of Record objects, return a list of Rename
        objects required to re-order the records according to position
        in the list.'''

        # our work list of Rename objects
        rename_list = []

        for index, record in enumerate(records, start=1):

            # are we already at the specified index?
            if index == record.number:
                continue

            rename_list.append(RecordRename(record, index))

        return rename_list

    @classmethod
    def _process_rename_list(clz, rename_list):
        '''Executes a list of Rename objects such that there are no
        conflicts (overwrites).'''

        # here we're treating the rename_list like a queue
        while rename_list:

            rename = rename_list.pop()

            if not rename.conflict:

                rename.execute()
                continue

            #
            # deal with conflicts
            #

            # the existing name
            old_name = rename.record.fullname

            # the name we _want_ to rename to, but can't because
            #  a file of that name already exists
            wanted_name = rename.record.new_name(rename.new_index)

            # our temporary name
            temp_name = 'PRIOR_TEMP_PREFIX_{}'.format(wanted_name)

            rename_to_temp = Rename(old_name, temp_name)
            temp_to_original = Rename(temp_name, wanted_name)

            # next work item is to rename the existing file to a
            #  temporary one
            rename_list.append(rename_to_temp)

            # renaming from the temporary name to the wanted one
            #  is deferred to the end of the queue
            rename_list.insert(0, temp_to_original)

    def up(self, record):
        '''Decrement the index of the specified record.'''

        index = self.records.index(record)

        if index == 0:
            return

        self.records.insert(index-1, self.records.pop(index))

    def down(self, record):
        '''Increment the index of the specified record.'''

        index = self.records.index(record)

        self.records.insert(index+1, self.records.pop(index))

    def top(self, record):
        '''Promote the specified record to index 01.'''

        index = self.records.index(record)

        self.records.insert(0, self.records.pop(index))

    def bottom(self, record):
        '''Demote the specified record to the highest index.'''

        index = self.records.index(record)

        self.records.append(self.records.pop(index))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('action', choices=Action._keymap.keys(),
                        help='available action')

    parser.add_argument('filename',
                        help='filename to move')

    args = parser.parse_args()

    action = Action.parse(args.action)

    target_file = args.filename

    if target_file.endswith('/'):
        target_file = target_file[0:-1]

    ledger = Ledger()

    record = ledger.get_record_by_name(target_file)

    ACTION_MAP = {
        Action.up: ledger.up,
        Action.down: ledger.down,
        Action.first: ledger.top,
        Action.last: ledger.bottom,
        Action.top: ledger.top,
        Action.bottom: ledger.bottom
    }

    ACTION_MAP[action](record)

    ledger.commit()
