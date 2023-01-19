## Local development
These are instruction to run unit tests and pylint locally.

### Install pylint

```
$ pip install pylint
```

### run pylint
```
$ find ./app2run -type f -name "*.py" | xargs pylint
```

### Intall py.test

```
$ pip install pytest
```

### run unit tests

Run the following (inside a virtual env with all dependencies installed).
```
$ py.test
```

Alternatively, run the following:
```
$ python3 -m pytest
```

To run all tests at of a specific file:

```
$ py.test -s $PATH_TO_FILE
```
e.g.
```
$ py.test -s app2run/commands/test_translate.py
```

To run a single unit test:

```
$ py.test -s $PATH_TO_FILE -k $TEST_CASE
```
e.g.
```
$ py.test -s app2run/commands/test_translate.py -k 'test_appyaml_not_found'
```

#### Debug a unit test
To debug a single unit test, use [caplog fixture](https://docs.pytest.org/en/7.1.x/how-to/logging.html#caplog-fixture) to enable logging and set logging level.

e.g.

```
def test_appyaml_not_found(caplog):
    """test_appyaml_not_found"""
    caplog.set_level(logging.INFO)
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['translate'])
        assert result.exit_code == 0
        logging.getLogger().info(f'result.output: {result.output}')
        assert "fake test failure" \
            in result.output
```

Run the test and get debug messages:

```
$ py.test -s app2run/commands/test_translate.py -k 'test_appyaml_not_found'
```
Output:
```
app2run/commands/test_translate.py:37: AssertionError
----------------------------------------------------------------------------- Captured log call ------------------------------------------------------------------------------
INFO     root:test_translate.py:36 result.output: app.yaml does not exist in current directory, please use --appyaml flag to specify the app.yaml location.
[Error] Failed to read input data.
```
