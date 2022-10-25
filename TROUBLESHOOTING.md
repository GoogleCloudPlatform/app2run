# Common errors

## Deployment failure: container failed to start
Error message:
```
ERROR: (gcloud.run.deploy) The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable. Logs for this revision might contain more information.
```

This error is commonly seen when deploying an application from source to Cloud Run, the likely causes of the errors are:
- Lack of or misconfiguration of `entrypoint` in the Cloud Run configuration.
- Dependencies/libraries used by the appliation are outdated and not compatible with Cloud Run.

In App Engine python runtime, when user didn't specify an `entrypoint` in app.yaml, an `entrypoint` is automoatically added to the config when building container from source, see https://cloud.google.com/appengine/docs/standard/python3/runtime#application_startup for more details.

On the other hand, Cloud Run uses [GCP Buildpacks](https://github.com/GoogleCloudPlatform/buildpacks) to build a container from source. To deploy an application to Cloud Run using buildpacks, users must explicitly specify an entrypoint for the application, see https://github.com/GoogleCloudPlatform/buildpacks#default-entrypoint-behavior.

### How to fix the error

Read about the [Cloud Run contract](https://cloud.google.com/run/docs/container-contract#port) regarding application host and port requirements.

If you know about the entrypoint to the application, add the entrypoint to the app.yaml or specifying it via the `--command` flag when running the `app2run translate` command.

If the App Engine application was deployed from source without an entrypoint specified at the app.ymal, the default entrypoint for Python application is `gunicorn -b :$PORT main:app` (also make sure `gunicorn` is added as a dependency at requirements.txt). For Ruby application, the default entrypoint is `bundle exec ruby app.rb -o 0.0.0.0`.

For Ruby applications that use [bundler](https://bundler.io/), please upgrade the bundler version to the newer version (>= 2.3.8), upgrade the sinatra dependency to a newer version (>= 2.2.0) and add webrick as a dependency (>= 1.7.0), see this [App Engine ruby application](https://github.com/GoogleCloudPlatform/ruby-docs-samples/tree/main/appengine/standard-hello_world) as an example.

See additional troubleshooting guide at https://cloud.google.com/run/docs/troubleshooting#container-failed-to-start.

