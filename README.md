## app2run
app2run is a CLI tool to assist migration of App Engine applications to run in
Cloud Run.

### Python versions supported
The app2run CLI tool is tested (unit tests passed) to run with the following Python versions:
- Python 3.10
- Python 3.9
- Python 3.8
- Python 3.7

## Installation

### Install python3
Download the latest python3 from https://www.python.org/downloads/ and install it based on your OS type (MacOS/Windows/Linux).

### Verify python version:
```
$ python3 --version
```
Example output
```
Python 3.10.4
```

### Install pip
Install `pip` following instructions at https://pip.pypa.io/en/stable/installation/. 

Verify pip is installed:

```
$ python3 -m pip --version
```
Example output
```
pip 22.0.4 from /Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/pip (python 3.10)
```

### Setup pip alias

Add the following line to local shell profile (e.g. `.zshrc` or `.bash_profile`):

```
alias pip="python3 -m pip"
```

### Set up $PATH
This step is needed for installing the `app2run` CLI tool in the later step, so that the locally compiled python CLI command (executable python script) is accessible locally. 

#### MacOS
Verify that `/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin` is at the `$PATH`, for example:
```
echo $PATH
/Library/Frameworks/Python.framework/Versions/3.10/bin:/Users/yulingz/google-cloud-sdk/bin:/usr/local/git/current/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin:/usr/local/go/bin 
```
If `/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin` is not in the `$PATH`, add it:
```
export PATH="/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin:$PATH" # replace PYTHON_VERSION with the actual python version number installed at your environment.
```

#### Linux
Verify that `$HOME/.local/bin` is at the `$PATH`, for example:
```
/usr/local/google/home/yulingz/.local/bin:/usr/lib/google-golang/bin:/usr/local/buildtools/java/jdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```
If `$HOME/.local/bin` is not in the `$PATH`, add it:
```
export PATH="$HOME/.local/bin:$PATH"
```

### (Alternatively) Use a Python virtual environment
You might want to use a Python virtual environment if you would like to test the CLI with a specific version of Python in an isolated environment.

#### Intall virtualenv
Follow this [instruction](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) to install `virtualenv` if not already done so.

#### Create a virtual environment:
```
virtualenv my_env -p $PATH_TO_PYTHON_VERSION_EXECUTABLE

e.g.

virtualenv py3.9 -p /usr/local/bin/python3.9
```

#### Activate a virtual environment:
```
source py3.9/bin/activate
```
#### Verify Python version:
```
python3 --version
```
#### Verify pip version:
```
python3 -m pip --version
```
Example output:
```
pip 22.1.2 from /usr/local/google/home/yulingz/pyenvs/py3.9/lib/python3.9/site-packages/pip (python 3.9)
```
Notice the pip package is at the virutual environment `/usr/local/google/home/yulingz/pyenvs/py3.9`.

#### Create a pip alias:
```
alias pip="python3 -m pip"
```

#### Exit a virtual environment (after done with testing):
```
deactivate
```
### Download and install app2run CLI
Download CLI source code:
```
$ git clone "sso://team/app-engine-geryon-team/app2run"
$ cd app2run
```
Install CLI (run command in the `app2run` source code root directory):
```
$ pip install --editable .
```
Verify CLI is installed:
```
$ app2run --help
```
Example output:
```
Usage: app2run [OPTIONS] COMMAND [ARGS]...

  app2run CLI.

Options:
  --help  Show this message and exit.

Commands:
  list-incompatible-features  List incompatible App Engine features to migrate
                              to Cloud Run.
  translate                   Translate an app.yaml to migrate to Cloud Run.
```
If you get the `command not found: app2run` error, verify the $PATH by following the **Set up $PATH** step.

### Testing the app2run CLI
In the application source code folder with app.yaml (if you don't already have an App Engine app, you could also use one of the [e2e test apps in App Egnine Flex](http://google3/apphosting/flex/e2e/apps/)), run the `list-incompatible-features` command to identify incompatible features:
```
$ app2run list-incompatible-features
```
Example output:
```
summary:
  major: 3
incompatible_features:
- path: runtime_config.python_version
  reason: 4 is not a known value for runtime_config.python_version.
  severity: unknown
- path: network.forwarded_ports
  reason: Cloud Run does not support port forwarding. No clients can connect to the
    app using the forwarded ports.
  severity: major
- path: resources.memory_gb
  reason: Cloud Run supports max 32Gi of memory.
  severity: major
```

Test the `translate` command, run:
```
$ app2run translate
```
Example output:
```
Your active configuration is: [prod]
Warning:not all configuration could be translated,
for more info use app2run list–incompatible-features.

gcloud run deploy foo-service \
  --concurrency=1000 \
  --timeout=60m \
  --cpu=5 \
  --memory=32Gi \
  --command="gunicorn -b :$PORT main:app" \
  --set-env-vars="foo=bar" \
  --service-account=yulingz-demo@appspot.gserviceaccount.com
```

## Local development

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


### Post for code review
```
$ git push origin HEAD:refs/for/main
```
