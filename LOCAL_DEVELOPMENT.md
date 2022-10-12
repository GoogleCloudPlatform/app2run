## Local development
These are instruction to run unit tests and pylint locally.

### Intall py.test

```
$ pip install pytest
```
### Install pylint

```
$ pip install pylint
```

### run unit tests

```
$ py.test
```
### run pylint
```
$ find . -type f -name "*.py" | xargs pylint
```
