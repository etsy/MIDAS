#!/usr/bin/env python
"""
This file exposes a class that you can use for simple data aggregation and
analytics. The naming of this file should inspire fun and laughter rather than
hatred and anger.
"""

from helpers.utilities import diff
from copy import copy


class DataScience():
    """This is the main class for the data_science utility"""

    def __init__(self, orm_object, new_data, tablename, key="name",
                 all_data=None):
        self.orm = orm_object
        self.new_data = new_data
        self.tablename = tablename
        self.key = key

        if not all_data:
            self.all_data = self.orm.select(self.tablename)
        else:
            self.all_data = all_data

    def get_all(self):
        """get_all is a simple wrapper around new, changed and removed
        entries"""
        self.get_new_entries()
        self.get_changed_entries()
        self.get_removed_entries()

    def find_in_data(self, data, column, value):
        """find_in_data finds given subdata in data and returns None if it's
        not there"""
        if not data or not column or not value:
            return None
        for i in data:
            if i[column] == value:
                return i
        return None

    def get_new_entries(self):
        """get_new_entries returns all new entries in a given dataset"""
        new_entries = []
        if self.new_data:
            for i in self.new_data:
                data = self.find_in_data(self.all_data, self.key, i[self.key])
                if not data:
                    new_entries.append(i)

        for i in new_entries:
            master = 'ty_name="%s" ' % (self.tablename, )
            for key, value in i.iteritems():
                if value != "KEY DNE":
                    master += '%s="%s"' % (key, value)
            self.orm.insert(self.tablename, i)
            print master
        return new_entries

    def __master_string(self, tablename, key):
        """master_string is an internal helper for generating a log ling"""
        return 'ty_name="%s" name="%s" changed_entry="true"' % (
            tablename, key)

    def __diff_string(self, changed_field, i_key, data, key, diff_string):
        """diff_string is an internal helpers for get_changed_entries"""
        master = ' %s="%s" %s_old="%s" %s_last_updated="%s"' % (
            changed_field,
            i_key,
            changed_field,
            data[key],
            changed_field,
            data["date"],)
        if diff_string != [data[key], i_key]:
            master += ' %s_diff_added="%s" %s_diff_removed="%s"' % (
                changed_field,
                diff_string[0],
                changed_field,
                diff_string[1],)
        return master

    def get_changed_entries(self):
        """
        get_changed_entries returns all changed entries in a given dataset
        """
        if self.new_data and self.all_data:
            for i in self.new_data:
                try:
                    data = self.find_in_data(
                        self.all_data,
                        self.key,
                        i[self.key]
                    )
                except IndexError:
                    continue
                if data:
                    data_copy = {}
                    for key, value in data.iteritems():
                        if not key.startswith("_") and key != "date":
                            data_copy[key] = value
                    i_copy = copy(i)
                    del(i_copy["date"])

                    if i_copy != data_copy:
                        master = self.__master_string(
                            self.tablename, i_copy[self.key]
                        )
                        data["date"] = i["date"]
                        for key, value in i_copy.iteritems():
                            if i[key] != data[key]:
                                changed_field = key
                                diff_string = diff(str(i[key]), str(data[key]))
                                string = self.__diff_string(
                                    changed_field,
                                    i[key],
                                    data,
                                    key,
                                    diff_string,
                                )
                                data[key] = i[key]
                                master += string
                        print master
                        self.orm.update(data)

    def get_removed_entries(self):
        """get_removed_entries return all removed entries in a given dataset"""
        if self.all_data and self.new_data:
            for i in self.all_data:
                data = self.find_in_data(self.new_data, self.key, i[self.key])
                if not data:
                    master = 'ty_name="%s" removed_entry="true" ' % (
                        self.tablename,)
                    for key, value in i.iteritems():
                        if value != "KEY DNE" and not key.startswith("_"):
                            master += '%s="%s" ' % (key, value)
                    print master
                    self.orm.delete(i)
