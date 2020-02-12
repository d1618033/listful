# listful

[![pypi](https://badge.fury.io/py/listful.svg)](https://pypi.org/project/listful)
[![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://pypi.org/project/listful)
[![Downloads](https://img.shields.io/pypi/dm/listful.svg)](https://pypistats.org/packages/listful)
[![Build Status](https://travis-ci.org/d1618033/listful.svg?branch=master)](https://travis-ci.org/d1618033/listful)
[![Code coverage](https://codecov.io/gh/d1618033/listful/branch/master/graph/badge.svg)](https://codecov.io/gh/d1618033/listful)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Description

Efficient filtering of lists of objects

## Installation

    pip install listful

## Usage


Initialize with the fields you want to filter by:
```
>>> from listful import Listful
>>> data = Listful(
...    [{'x': 1, 'y': 10}, {'x': 2, 'y': 20}, {'x': 2, 'y': 30}], 
...    fields=['x', 'y']
... )
```

### Filtering:

* By one field:
```
>>> data.filter(x=1).one_or_none()
{'x': 1, 'y': 10}
>>> data.filter(y=20).one_or_none()
{'x': 2, 'y': 20}
```

* By one field, with more than one result:
```
>>> data.filter(x=2).to_list()
[{'x': 2, 'y': 20}, {'x': 2, 'y': 30}]
```

* By two fields:
```
>>> data.filter(x=2, y=30).one_or_none()
{'x': 2, 'y': 30}
```

* Raise exception if more than one found
``` 
>>> data.filter(x=2).one_or_raise()
Traceback (most recent call last):
<...>
listful.exceptions.MoreThanOneResultException: Found more than one result for filter {'x': 2}: [{'x': 2, 'y': 20}, {'x': 2, 'y': 30}]
```

* Get all values for a specific field

```
>>> data.get_all_for_field('x')
[1, 2, 2]
```

### Updating indexes:

`Listful` has the same api as `list`, so you can get/set/delete items the same way 
and the indices will be updated automatically

```
>>> data[0] = {'x': 17, 'y': 17}
>>> data.filter(x=17).one_or_none()
{'x': 17, 'y': 17}
>>> data[0]
{'x': 17, 'y': 17}
>>> del data[0]
>>> data.filter(x=17).one_or_none()
``` 

If you want to modify an element and update the indices you can do so explicitly:
```
>>> data[0]['x'] = 1
>>> data.rebuild_indexes_for_item(data[0])
>>> data.filter(x=1).one_or_none()
{'x': 1, 'y': 20}
``` 


### Objects:

Listful supports also lists of objects:

```
>>> class Item:
...     def __init__(self, x, y):
...         self.x = x
...         self.y = y
...
...     def __repr__(self):
...         return f"Item(x={self.x}, y={self.y})"

>>> items = Listful(
...    [Item(x=1, y=10), Item(x=2, y=20), Item(x=2, y=30)], 
...    fields=['x', 'y']
... )
>>> items.filter(x=1).one_or_none()
Item(x=1, y=10)
```
## For developers

### Create venv and install deps

    make init

### Install git precommit hook

    make precommit_install

### Run linters, autoformat, tests etc.

    make pretty lint test

### Bump new version

    make bump_major
    make bump_minor
    make bump_patch

## License

MIT

## Change Log

Unreleased
-----

* ...

0.1.1 - 2020-02-12
-----

* ...

0.1.0 - 2020-02-12
-----

* initial
