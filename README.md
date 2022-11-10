# app2run

`app2run` is a Python CLI tool to assist the migration of App Engine applications to run in Cloud Run. The app2run tool translates your App Engine [app.yaml](https://cloud.google.com/appengine/docs/standard/reference/app-yaml?tab=python#top) file or a deployed App Engine app into a comparable Cloud Run [service configuration ](https://cloud.google.com/run/docs/deploying)with minimal changes.


## Supported App Engine runtimes

The `app2run` CLI tool supports the following App Engine runtimes:

*   [App Engine Standard Gen2 runtimes](https://cloud.google.com/appengine/docs/standard/runtimes)
*   [App Engine Flex runtimes](https://cloud.google.com/appengine/docs/flexible)

Note: The app2run tool doesn’t support App Engine Standard Gen1 runtimes. 


## Set up your development environment

Install the following dependencies for the app2run CLI:

1. Gcloud CLI
2. Python runtime environment (version 3.7+)

### Install the `gcloud CLI`

The gcloud CLI is a set of tools to create and manage Google Cloud resources. You can use these tools to deploy apps, manage authentication, customize local configuration, and perform other tasks from the command line. To install the gcloud CLI, see [Install the Google Cloud CLI](https://cloud.google.com/sdk/docs/install-sdk).


### Specify dependencies for Python 3 

To run the `app2run` tool, you must have a Python 3 interpreter of version Python 3.7 or newer, and Pip installed on your local machine (successful unit tests in versions 3.7+).

If you already have Python 3 (or virtualenv) and pip installed, skip to the [Install app2run CLI section](https://github.com/GoogleCloudPlatform/app2run#app2run_install).

1. Install Python3
2. Install Pip
3. Setup pip alias
4. Set up $PATH
5. (Optional) Use a Python virtual environment

#### Install Python 3

Download the latest Python 3 from https://www.python.org/downloads/ and install it based on your OS type (MacOS/Windows/Linux). 

To verify that Python is available, run the following command:

  ```
  $ python3 --version
  ```


  Example output


  ```
  Python 3.10.4
  ```


#### Install pip

Install `pip` following instructions at https://pip.pypa.io/en/stable/installation/.

To verify that pip3 is available, run the following command:


  ```
  $ python3 -m pip --version
  ```


  Example output


  ```
  pip 22.0.4 from /Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/pip (python 3.10)

```
#### Setup pip alias

Set up an alias for pip to ensure you always use Python 3.

Add the following line to local shell profile. Example: `.zshrc` or `.bash_profile`.


```
alias pip="python3 -m pip"
```

#### Set up $PATH

To access the locally compiled Python CLI command, set up the $PATH variable. This is a required step for installing the app2run CLI tool. 

For MacOS, 

* Verify that `/Library/Frameworks/Python.framework/  Versions/PYTHON_VERSION/bin` is at the `$PATH`. 

  Example:

  ```
  $ echo $PATH
  /Library/Frameworks/Python.framework/Versions/3.10/bin:/usr/local/git/current/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin 

  ```


* If `/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin` is not in the `$PATH`, add it.
  Example: 

  ```
  # replace PYTHON_VERSION with the actual python version number installed at your environment.

  $ export PATH="/Library/Frameworks/Python.framework/Versions/PYTHON_VERSION/bin:$PATH" 
  ```
For Linux,

* Verify that `$HOME/.local/bin` is at the `$PATH`.

  Example:

  ```
  /home/$USER/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

  ```
* If `$HOME/.local/bin` is not in the `$PATH`, add it.

  Example:

  ```
  export PATH="$HOME/.local/bin:$PATH"
  ```



#### (Optional) Use a Python virtual environment

You can use a Python virtual environment to test the CLI with a specific version of Python in an isolated environment. For instructions on installing, and creating a virtual environment, see [Installing virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-virtualenv).


## Install app2run CLI

1. Download the source code for the app2run CLI tool. 

    ```
    $ git clone "https://github.com/GoogleCloudPlatform/app2run"
    $ cd app2run
    ```

2. Install the CLI (run command in the `app2run` source code root directory)

    ```
    $ pip install --editable
    ```

3. Verify CLI is installed

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
      list-incompatible-features  List App Engine features incompatible with Cloud Run.
      translate                   Translate an app.yaml / deployed app engine app for deploying with Cloud Run.

    ```

If you get the `command not found: app2run` error, verify your $PATH is [set to your Python installation.](https://github.com/GoogleCloudPlatform/app2run#setup_path).


## Translate your App Engine app.yaml configuration to Cloud Run configuration

To use the App engine app.yaml as the input, run the following commands from the root directory of your App Engine app where your `app.yaml` is located, or use the `--appyaml` flag to provide the complete file path for app.yaml. Example:` $HOME/~src/app.yaml`.
To translate your local `app.yaml` file:

1. Run the `app2run list-incompatible-features` command to check for incompatible features in your app’s configuration. 

    ```
    $ app2run list-incompatible-features -h

    # Assumes app.yaml is in the current working directory
    $ app2run list-incompatible-features
    ```
    or

    ```
    # app.yaml from a directory other than the current working directory
    $ app2run list-incompatible-features --appyaml=PATH_TO_APP_YAML
    ```

    Example output:
    The output indicates severity level. A severity level of `major` shows that your translated config file isn’t compatible with the Cloud Run service. For a list of incompatible features, see [app2run config](https://github.com/GoogleCloudPlatform/app2run/blob/main/app2run/config/features.yaml). 

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
      
      Use the `-o html` flag to get the same output in HTML format. Example:

      ```
      $ app2run list-incompatible-features -o html
      list-incompatible-features output for app.yaml:

      Html output of incompatible features: /tmp/tmpgxu_myaq/incompatible_features.html
      ```

2. Run the `app2run translate` command. The `--target-service` allows you to override the inferred service name of your App Engine’s local `app.yaml`. 

    ```
    $ app2run translate -h

    # from source code directory w/ app.yaml
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


    From the app source code root directory, run the `glcoud run deploy` command from the above `app2run translate` output. 
    
    Example:


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



## Translate the service configuration of a deployed App Engine service to a Cloud Run service.

Besides using `app.yaml` as an input, you can use a deployed App Engine app's version configuration for translation. 

The `gcloud app versions describe` outputs the metadata of a deployed App Engine version.

1. Identify a deployed App Engine app version for translation.

    ```
    $ gcloud app versions list
    ```

2. Use `app2run list-incompatible-features` to to check for incompatible features in your deployed version configuration .

    ```
    $ app2run list-incompatible-features --service SERVICE_NAME --version VERSION_ID --target-service my-service
    ```

3. Run the `app2run translate` command. The `--target-service` allows you to override the inferred service name of your  deployed App Engine app version. 

    ```
    $ app2run translate --service SERVICE_NAME --version VERSION_ID --target-service my-service
    ```

4. Run the `gcloud run deploy` command generated from `app2run translate`.
From the app's source code root directory, execute the `gcloud run deploy` command from the app2run translate output. This step is the same as using `app.yaml` as an input in the previous section.


## Report bug/feature request/feedback.

Feedback is welcome, please file an issue [here](https://github.com/GoogleCloudPlatform/app2run/issues).


