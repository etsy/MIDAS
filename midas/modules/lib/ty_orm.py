#!/usr/bin/env python
"""
This is MIDAS' lightweight ORM
"""

import sqlite3
from helpers.utilities import to_ascii

class TyORM():
    """
    This is Tripyarn's lightweight ORM class
    """

    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def commit(self):
        """commit is a simple wrapper around self.conn.commit()"""
        self.conn.commit()

    def raw_sql(self, sql, params=None):
        """raw_sql executes raw SQL provided to it in the 'sql' parameter"""
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        fetchall = self.cursor.fetchall()
        self.commit()
        return fetchall

    ###########################################################################
    # Create / alter table methods
    ###########################################################################

    def parse_attr(self, attr):
        """parse_attr parses table attributes"""
        i = attr.keys()[0]
        sql_col = "\"%s\" %s" % (i, attr[i]['type'])
        try:
            if attr[i]["default"]:
                sql_col += " DEFAULT %s" % attr[i]["default"]
        except KeyError:
            pass
        try:
            if not attr[i]["nullable"]:
                sql_col += " NOT NULL"
        except KeyError:
            pass
        try:
            if attr[i]["attrs"]:
                sql_col += " %s" % attr[i]["attrs"]
        except KeyError:
            pass
        try:
            if attr[i]["primary_key"]:
                sql_col += " PRIMARY KEY"
        except KeyError:
            pass
        return sql_col

    def create_table(self, table_name, attrs):
        """create_table create a table defined by a supplied table name and
        table attributes"""
        sql = "CREATE TABLE IF NOT EXISTS \"%s\"(\n\t" % table_name
        sql += "\"id\" integer PRIMARY KEY,\n\t"
        for attr in attrs:
            i = {attr : attrs[attr]}
            sql += self.parse_attr(i)
            sql += ",\n\t"
        sql = sql.strip(",\n\t")
        sql += "\n);"
        self.raw_sql(sql)

    def alter_table(self, table_name, attrs):
        """alter_table alters a given table based on a supplied table name and
        potentially updated table attributes"""
        sql = "PRAGMA table_info(\"%s\")" % table_name
        table_info = self.raw_sql(sql)
        db_cols = []
        new_cols = attrs.keys()
        for each in table_info:
            db_cols.append(each[1])
        alter_cols = list(set(new_cols) - set(db_cols))

        sql = "ALTER TABLE \"%s\" ADD COLUMN " % table_name

        new_attrs = {}
        for i in attrs:
            if i in alter_cols:
                new_attrs[i] = attrs[i]
                alter_sql = "%s%s%s" % (sql, self.parse_attr(new_attrs), ";")
                self.raw_sql(alter_sql)
                new_attrs = {}

    def create_index(self, indexes):
        """create_index creates a supplied index on a given table"""
        for index in indexes:
            sql = "CREATE INDEX IF NOT EXISTS %s;" % index
            index = self.raw_sql(sql)

    def initialize_table(self, table_name, attrs, indexes=None):
        """initialize_table creates the table if it doesn't exist, alters the
        table if it's definition is different and creates any indexes that it
        needs to if they don't already exist"""
        self.create_table(table_name, attrs)
        self.alter_table(table_name, attrs)
        if indexes:
            self.create_index(indexes)

    ###########################################################################
    # Create methods
    ###########################################################################

    def insert(self, table_name, data):
        """insert is your basic insertion method"""
        data = to_ascii(data)
        if data is None:
            return None
        sql = "INSERT INTO %s" % table_name
        sql += "(id, %s) VALUES" % ', '.join(data.keys())
        sql += "(NULL, "
        sql += ', '.join(['?'] * len(data.values()))
        sql = "%s);" % sql
        params = data.values()
        self.raw_sql(sql, params)

    ###########################################################################
    # Read methods
    ###########################################################################
    def __parse_columns(self, table_name, columns):
        """internal helper for column parsing"""
        select_columns = []
        if columns is None or columns == "*":
            sql = "PRAGMA table_info(\"%s\");" % table_name
            results = self.raw_sql(sql)
            columns = []
            for result in results:
                columns.append(result[1])
        if type(columns) is list:
            select_columns = columns
        elif type(columns) is str:
            columns = columns.replace(" ", "").split(",")
            select_columns = columns

        if type(select_columns) is list and select_columns:
            select_columns = ', '.join(select_columns)

        original_columns = []
        for i in columns:
            original_columns.append("_%s" % i)

        return columns, select_columns, original_columns

    def select(self, table_name, columns=None, where=None, limit=None, \
        order_by=None):
        """select is your basic selection method"""

        columns, select_columns, original_columns = self.__parse_columns(
            table_name,
            columns
        )

        sql = "SELECT %s FROM \"%s\"" % (select_columns, table_name)

        parameterized_attrs = None
        if where is not None:
            if type(where) is not list:
                sql += " WHERE %s" % where
            else:
                sql += "WHERE %s" % where[0]
                parameterized_attrs = where[1]

        if limit is not None:
            sql += " LIMIT %s" % limit

        if order_by is not None:
            sql += " ORDER BY %s" % order_by

        sql += ";"

        if not parameterized_attrs:
            results = self.raw_sql(sql)
        else:
            results = self.raw_sql(sql, parameterized_attrs)

        return_values = []

        for i in results:
            data = dict(zip(columns, i))
            if 'id' in data:
                del(data['id'])
            final_data = dict(
                data.items() +\
                dict(zip(original_columns, i)).items() + \
                {"_table": table_name}.items()
            )
            return_values.append(final_data)

        if not return_values:
            return None
        return return_values

    ###########################################################################
    # Update methods
    ###########################################################################

    def update(self, data):
        """update is your basic update method"""
        data = to_ascii(data)
        if data is None:
            return None
        original_data = {}
        updated_data = {}
        for i in data:
            if i.startswith("_") and i != "_table" and i != "_id":
                original_data[i] = data[i]
            else:
                updated_data[i] = data[i]

        to_change = {}
        for i in updated_data:
            if i != "_table" and i != "_id":
                if updated_data[i] != original_data["_%s" % i]:
                    to_change[i] = updated_data[i]

        sql = "UPDATE \"%s\" SET" % data["_table"]

        if not to_change:
            return None

        for i in to_change:
            sql += " %s=?," % i

        sql = sql.strip(",")

        sql += " WHERE id = ?;"

        params = to_change.values()
        params.append(data["_id"])

        self.raw_sql(sql, params)

    ###########################################################################
    # Delete methods
    ###########################################################################

    def delete(self, data):
        """delete is your basic deletion method"""
        data = to_ascii(data)
        if data is None:
            return None
        if type(data) == dict:
            sql = "DELETE FROM \"%s\" WHERE id = ?;" % data["_table"]
            self.raw_sql(sql, [data["_id"]])
            return
        elif type(data) == list:
            tables_and_ids = {}
            for i in data:
                table = i["_table"]
                if table not in tables_and_ids:
                    tables_and_ids[table] = []
                tables_and_ids[table].append(i["_id"])
            for k, j in tables_and_ids.iteritems():
                sql = "DELETE FROM \"%s\" WHERE id IN (%s);" % (
                    k,
                    ', '.join(['?']*len(j))
                )
                self.raw_sql(sql, j)
