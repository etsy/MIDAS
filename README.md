MIDAS
=====

MIDAS is a framework for developing a Mac Intrusion Detection Analysis System,
based on work and collaborative discussions between the Etsy and
Facebook security teams. This repository provides a modular framework and a
number of helper utilities, as well as an example module for detecting
modifications to common OS X persistence mechanisms.

The MIDAS project is based off concepts presented in [Homebrew Defensive
Security] (http://www.slideshare.net/mimeframe/ruxcon-2012-15195589) and
[Attack-Driven Defense]
(http://www.slideshare.net/zanelackey/attackdriven-defense), as well as
lessons learned during the development of the Tripyarn and BigMac products.

Our mutual goal in releasing this framework is to foster more discussion in
this area and provide organizations with a starting point in instrumenting
OS X endpoints to detect common patterns of compromise and persistence.

Overview
---------

The `midas` subdirectory is where the core MIDAS code lives. The entry point is
`launcher.py`. From there, each module in `midas/modules` is executed and the
stdout of the module is written to a log file. When deploying MIDAS, this is
the code that's put on user's systems.

The `develop` subdirectory is where development resources (like a `.pylintrc`)
live.

The `templates` resource is where template and base resources live. These can be
used as a starting point when adding modules.

Architecture
------------

MIDAS allows you to define a set of "modules" that implement
host-based checks, verifications, analysis, etc.

### Launcher

The `launcher.py` file exists at the top level of the `midas` directory. It
gathers some simple information about the host it's executing on (such as time,
hostname, etc) and defines the ways that it should handle modules of certain
languages. To add a supported language, create a new instance of
`TyLanguage` in `launcher.py` and add it to the `SUPPORTED_LANGUAGES` list. If
you'd like to change the way a certain language is supported (perhaps you'd
like all python modules to be executed with a custom version of python), you
can change the attributes (such as `execution_string`) of the language.

Once key definitions are made, the launcher will iterate through all files
(note that directories are explicitly skipped) in the `modules` subdirectory.
For each file in the directory, if a language entry is found that indicates
how to deal with that filetype, the file is executed and the stdout of the
module are appended to a log file in the `log` subdirectory. Note that a
module `modules/example.py` will generate a log file `logs/example.log`.

### Module language

Modules can be written in any language, so long as a named tuple for that
language is defined in `midas/launcher.py`. These named tuples (which
already exist for python, ruby and shell) exist so that MIDAS knows how
to handle certain filetypes when it sees them.

As long as your code can be executed and prints something to stdout, it can be
a module.


Components
----------

### Example module

The file `midas/modules/example.py` is an example MIDAS module created to
illustrate what a MIDAS module might look like. This module performs
analysis of LaunchAgents and LaunchDaemons on the host and logs any
modifications that it identifies. The rest of the checks and
verifications analyze the host firewall configurations and log any additions or
differences that are identified. **This is not meant to be a complete intrusion
detection mechanism alone**, instead it is meant as a reference example of what
a MIDAS module may look like.

### Helpers

There are several helper files in `midas/lib/helpers` that are generally
grouped by category. Functions in these helpers can be imported by modules to
assist in general tasks. Some functionality exposed by helpers include:

- list all weak SSH keys on a host
- find all files in a given directory with given permissions
- list all startup items
- list all LaunchAgents, LaunchDaemons, etc.
- list and hash all kernel extensions
- return the SSID of the currently connected WiFi network
- return the IP and MAC address of the current network gateway
- return DNS configuration information
- and much, much more

### Config system

The config file, which can be found at `midas/lib/config.py` is a way to group
together information that can be abstracted away from modules. Usually there
are things like strings that should be checked in a certain module validation,
directories to search during a given check, etc. By abstracting the data away
from the individual module/code, it makes it easier for people who might not
maintain the code to contribute to it.

Since the config dictionary is operated on via a static method, it does not
need to instantiate the Config object in order to use it. To add a new value
to the config dictionary, simply add an entry in the class.

### ORM and table definitions

MIDAS relies on a local datastore to do some simple host-based analytics with
the data gathered by modules. For this reason, MIDAS comes with a simple,
custom ORM.

#### Table definitions

Table schemas are described via a simple dictionary, all of which can be found
in `midas/lib/tables/`. The dictionary is then parsed and valid SQL is created
from the dictionary. Each item in the dictionary represents a column. The
column definition should be a key-value pair where the key is a strings that
represents the name of the column and the value is a dictionary that describes
the column. The column definition dictionary can have the following attributes:

- default
  - If this is set, it will be the default value of the column. This is most frequently set to `"NULL"`
- nullable
  - If this is set to `False`, then the `NOT NULL` attribute will be used when creating the table
- attrs
  - Use this to add additional SQL syntax that you want added to the table creation statement that isn't supported by tyORM
- primary_key
  - If this is set to `True`, then the column listed will be set to the primary key

See the following same table definition for reference:

```python
test_table = {
    "data_field_name" : {
        "type" : "text",
        "nullable" : False,
    },
    "other_data_field" : {
        "type" : "text",
        "default" : "NULL",
    }
}
```

#### Instantiating an ORM object

When instantiating an ORM object, the class takes one parameter: the database
filename. If the file doesn't exist, the ORM will create it.

See the following example code for reference:

```python
from lib.ty_orm import TyORM
ORM = TyORM("midas_hids.db")
```

#### Transparent primary key system

Although it is possible to specify a primary key when creating a table, TyORM
transparently creates an auto-incrementing `id` column and sets it as a primary
key. Although SQLite allows you to specify several primary keys, this is not
necessary. The `id` column is always used as the `WHERE` clause identifier when
doing `UPDATE` and `DELETE` operations.

#### Creating

Use the `insert` method to insert data into a table. The `insert` method takes
two arguments: the table name and the data that you'd like to insert. The table
name should be a string that describes the name of the table. The data should
be a dictionary such that the keys describe the columns that the value should
be inserted into.

See the following example `insert` call for reference:

```python
ORM = TyORM("midas_hids.db")
data = {
    "data_field_name" : "foo",
    "other_data_field" : "bar",
}
ORM.insert("test_table", data)
```

#### Reading

Use the `select` method to read data from the database. The `select` method takes one mandatory argument and three optional arguments.

The mandatory argument that all `select` method calls needs to have is the table name that you'd like to select from. The optional arguments are as follows:

- columns
  - An array of columns that you would like returned
- where
  - A string that describes the "WHERE" clause that you would like added to the SQL query
  - Note that this can be a string but if you're supplying user input, this should be an array such that the first item in the array is the where clause with '?' place holders and the second item in the array is an array with the representative values.
- limit
  - An integer describing the LIMIT value that you would like added to the SQL query
- order_by
  - A string dictating which column to order results by

See the following example `select` calls for reference:

```python
ORM = TyORM("midas_hids.db")

# this will return all table data
ORM.select("test_table")

# this will return only the "data_field_name" column of the
# first five columns where the "data_field_name" column is "foobar", ordered by "data_field_name"
ORM.select("test_table", ["data_field_name"], "data_field_name = 'foobar'", 5, "data_field_name")
```

#### Updating

Use the `update` method to update data from the database. Simply `select` some
data and change the returned dictionary to reflect the data you want the field
to be updated to and, via some "hidden" values, the ORM will take care of the
rest.

See the following example `update` call for reference:

```python
ORM = TyORM("midas_hids.db")
data = ORM.select("test_table", "*", "data_field_name = 'foobar123'", 1)
data['data_field_name'] = 'newname123'
ORM.update(data)
```

#### Deleting

Use the `delete` method to delete data from the database. Simply `select` some
data and call the delete method and the ORM will take care of the rest.

See the following example `delete` call for reference:

```python
ORM = TyORM("midas_hids.db")
data = ORM.select("test_table", "*", "data_field_name = 'foobar123'", 1)
ORM.delete(data)
```

#### Initializing tables and dynamic ALTERs

One of the strengths of tyORM is it's ability to dynamically ALTER a table if
the table's schema doesn't match the table  definition dictionary.

Simply call the `initialize_table` table method before operating on the table.
The `initialize_table` method takes two arguments: the table name and the table
definition. The `initialize_table` method will create the table if it doesn't
exist and it will alter the table if any new columns have been added.

See the following example code for reference:

```python
test_table_data = {
    "data_field_name" : "foo",
    "other_data_field" : "bar",
}

ORM = TyORM("midas_hids.db")
ORM.initialize_table("test_table", test_table_data)

# operate on the ORM here
```

Due to limitations of SQLite, this only support new columns that are added, not
columns that are removed.

### Host based analytics

The file `lib/data_science.py` is used for simple host based data aggregation.
The `DataScience` class is used to query the database and log any changes,
given a new dataset. Using data_science is very simple. The class constructor
takes three arguments:

- a TyORM object that is already instantiated with the database which is to be
  operated on
- a dataset
- a table name that the dataset should be compared against

The dataset should be an array of dictionaries. Each item in the array should
be a dictionary where each key of the dictionary represents a column in the
database and each corresponding value represents a corresponding value. It's
OK if some columns of the table are not in the dictionary, but the `name`
column should always be present. Although TyORM has it's own transparent
primary key system using the `id` column, for the sake of `data_science`, the
`name` column should be present and it should be unique. The `data_science`
code will then select all of the data from the given table and compare it
against the supplied dataset, printing out log lines illustrating all data that
has been added, removed and changed.

### Decorators

The file `midas/lib/decorators.py` contains a bunch of decorators that can be
used for a variety of things, but currently predominantly code execution
frequency.

### Property List parsing

This is the utility that MIDAS uses to operate on property list files such
as LaunchAgents and LaunchDaemons. This is mostly the
[biplist](https://github.com/wooster/biplist) python module, however, you
should never actually call any of the biplist functions directly.

The `read_plist` function is what you should call when trying to read a plist.
When you call `read_plist`, it first tries to use biplist's readPlist. That
code determines if the plist is a binary plist or an XML plist. If it is an XML
plist, it just uses python's plistlib to read the plist. If it is a binary
plist, it uses a native python implementation to parse it and return it's
contents. If that, for whatever reason, fails, the `read_plist` function will
then try to shell out to `plutil` to parse the plist.

The `get_plist_key` function takes a plist and a key as input. It returns the
key (if the key exists) or False if it does not. This is so that, when
operating on property lists, you don't have to roll your own exception handling
on every access.

`read_plist` and `get_plist_key` are the only two functions that should be
called from this file.

Customization
-------------

A MIDAS deployment in an organization typically follows these steps:

- Create a private fork of MIDAS
- Add modules and helpers that implement instrumentation specific to the environment
- Deploy the code (with updated modules) to OS X endpoints in the organization
- Set a crontab/LaunchAgent that executes MIDAS at a set interval
- Use syslog/a log aggregation mechanism to forward the logs to a central logging
  host
- Analyze the collected data and create alerts for anomalies

Contributors
------------

+ __Mike Arpaia__ ([@mikearpaia](https://twitter.com/mikearpaia))
+ __Chris Biettchert__ ([@chrisbiettchert](https://twitter.com/chrisbiettchert))
+ __Ben Hughes__ ([@benjammingh](https://twitter.com/benjammingh))
+ __Zane Lackey__ ([@zanelackey](https://twitter.com/zanelackey))
+ __mimeframe__ ([@mimeframe](https://twitter.com/mimeframe))
