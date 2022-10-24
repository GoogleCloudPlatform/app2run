## app2run
`app2run` is a Python CLI tool to assist migration of App Engine applications to run in
Cloud Run. It is intended to translate App Engine configuration into compatible Cloud Run configuration, and make it simple to deploy App Engine applications from source to Cloud Run with minimal changes.

### App Engine runtimes supported
The `app2run` CLI tool supports translating the following App Engine runtimes:
- [App Engine Standard Gen2 runtimes](https://cloud.google.com/appengine/docs/standard/runtimes)
- [App Engine Flex runtimes](https://cloud.google.com/appengine/docs/flexible)

### Report bug/feature request/feedback.
Feedback is welcome, please file an issue [here](https://github.com/GoogleCloudPlatform/app2run/issues).

## Install software dependencies
### Install `gcloud`
Follow the [gcloud installation guide](https://cloud.google.com/sdk/docs/install) to install `gcloud` in your environment. `gcloud` is used to deploy the application to Cloud Run.

### Install Python3
#### Python versions supported
The app2run CLI tool is tested (unit tests passed) to run with the following Python versions:
- Python 3.10
- Python 3.9
- Python 3.8
- Python 3.7

If you already have python3 (or virtualenv) and pip installed, skip over to the [Install app2run CLI](#app2run_install) step.
#### Install python3
Download the latest python3 from https://www.python.org/downloads/ and install it based on your OS type (MacOS/Windows/Linux).

#### Verify python version:
```
$ python3 --version
```
Example output
```
Python 3.10.4
```

#### Install pip
Install `pip` following instructions at https://pip.pypa.io/en/stable/installation/. 

Verify pip is installed:

```
$ python3 -m pip --version
```
Example output
```
pip 22.0.4 from /Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/pip (python 3.10)
```

#### Setup pip alias

Add the following line to local shell profile (e.g. `.zshrc` or `.bash_profile`):

```
alias pip="python3 -m pip"
```

#### Set up $PATH
<a name="setup_path"></a>
This step is needed for installing the `app2run` CLI tool in the later step, so that the locally compiled python CLI command (executable python script) is accessible locally. 

##### MacOS
Verify that `/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin` is at the `$PATH`, for example:
```
$ echo $PATH
/Library/Frameworks/Python.framework/Versions/3.10/bin:/usr/local/git/current/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin 
```
If `/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin` is not in the `$PATH`, add it:
```
# replace PYTHON_VERSION with the actual python version number installed at your environment.

$ export PATH="/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin:$PATH" 
```

##### Linux
Verify that `$HOME/.local/bin` is at the `$PATH`, for example:
```
/home/$USER/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```
If `$HOME/.local/bin` is not in the `$PATH`, add it:
```
export PATH="$HOME/.local/bin:$PATH"
```

#### (Alternatively) Use a Python virtual environment
You might want to use a Python virtual environment if you would like to test the CLI with a specific version of Python in an isolated environment.

##### Intall virtualenv
Follow this [instruction](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv) to install `virtualenv` if not already done so.

##### Create a virtual environment:
```
$ virtualenv my_env -p $PATH_TO_PYTHON_VERSION_EXECUTABLE
```
e.g.
```
$ virtualenv py3.9 -p /usr/local/bin/python3.9
```

##### Activate a virtual environment:
```
$ source py3.9/bin/activate
```
##### Verify Python version:
```
$ python3 --version
```
##### Verify pip version:
```
$ python3 -m pip --version
```
Example output:
```
pip 22.1.2 from /home/$USER/pyenvs/py3.9/lib/python3.9/site-packages/pip (python 3.9)
```
Notice the pip package is at the virutual environment ` /home/$USER/pyenvs/py3.9`.

##### Create a pip alias:
```
$ alias pip="python3 -m pip"
```

##### Exit a virtual environment (after done with testing):
```
$ deactivate
```
### Install app2run CLI
<a name="app2run_install"></a>

#### Download CLI source code:
```
$ git clone "https://github.com/GoogleCloudPlatform/app2run"
$ cd app2run
```

#### Install CLI (run command in the `app2run` source code root directory):
```
$ pip install --editable .
```

#### Verify CLI is installed:
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

If you get the `command not found: app2run` error, verify the $PATH by following the [Set up $PATH](#setup_path) step.

### Testing the app2run CLI with app.yaml as input
An App Engine app.yaml can be used as an input for the `app2run` CLI.

#### 1. Use the `app2run list-incompatible-features` command.

Learn about the `app2run list-incompatible-features` command API:
```
$ app2run list-incompatible-features -h
```

Check for incompatible features of an App (run command from the the GAE App source code root directory, or use the `--appyaml` flag to provide the file path for a `app.yaml`)

```
# from App source code directory w/ app.yaml
$ app2run list-incompatible-features
```

or 

```
$ app2run list-incompatible-features --appyaml=PATH_TO_APP_YAML
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

Use the `-o html` flag to get the same output in HTML format, e.g.:

```
$ app2run list-incompatible-features -o html
list-incompatible-features output for app.yaml:

Html output of incompatible features: /tmp/tmpgxu_myaq/incompatible_features.html
```

#### 2. Use the `app2run translate` command.
Learn about the `app2run translate` command API:
```
$ app2run translate -h
```
Translate an App (run command from the GAE App source code root directory,
or use the `--appyaml` flag to provide the file path for a `app.yaml`), `--target-service` is used to specify a custom name for the target Cloud Run service:

```
# from source code directory w/ app.ayml
$ app2run translate --target-service my-service
```

or

```
$ app2run translate --appyaml PATH_TO_APP_YAML --target-service my-service
```
Example output:
```
Your active configuration is: [prod]
Warning:not all configuration could be translated,
for more info use app2run list–incompatible-features.

gcloud run deploy my-service \
  --concurrency=1000 \
  --timeout=60m \
  --cpu=4 \
  --memory=32Gi \
  --command="gunicorn -b :$PORT main:app" \
  --set-env-vars="foo=bar" \
  --service-account=$PROJECT_ID@appspot.gserviceaccount.com
```

From the app source code root directory, execute the `glcoud run deploy` command from the above `app2run translate` output, e.g.:

```
$ gcloud run deploy my-service \
  --concurrency=1000 \
  --timeout=60m \
  --cpu=4 \
  --memory=32Gi \
  --command="gunicorn -b :$PORT main:app" \
  --set-env-vars="foo=bar" \
  --service-account=$PROJECT_ID@appspot.gserviceaccount.com
Deploying from source. To deploy a container use [--image]. See https://cloud.google.com/run/docs/deploying-source-code for more details.
...
Building using Buildpacks and deploying container to Cloud Run service [my-service] in project XXX region XXX
✓ Building and deploying new service... Done.
  ✓ Uploading sources...
  ✓ Building Container... Logs are available at [XXX].
  ✓ Creating Revision... Deploying Revision.
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
Service [my-service] revision [my-service-00001-zob] has been deployed and is serving 100 percent of traffic.
Service URL: https://my-service-f5pup6wzca-uc.a.run.app
```

### Testing the app2run CLI with a deployed App Engine version as input.

Besides using `app.yaml` as an input, the app2run CLI could take a deployed App Engine version as an input. Under the hood, it uses `gcloud app versions describe` command to get the metadata of a deployed App Engine version, and runs the same logics (as `app.yaml` as input) to list incompatible features and translate the App.

#### 1. Identify a deployed App Engine version for translation:

```
$ gcloud app versions list
```

#### 2. Use `app2run list-incompatible-features` on a deployed version.

```
$ app2run list-incompatible-features --service SERVICE_NAME --version VERSION_ID --target-service my-service
```

#### 3. Use `app2run translate` on a deployed version.
```
$ app2run translate --service SERVICE_NAME --version VERSION_ID --target-service my-service
```
#### 4. Run the `gcloud run deploy` command generated from `app2run translate`.
From the app source code root directory, execute the `glcoud run deploy` command
from the `app2run translate` output. This step is the same as using `app.yaml` as an input.
