## app2run
app2run is a CLI tool to assist migration of App Engine applications to run in
Cloud Run.

## Local testing
```
pip install --editable .

cat << EOF > app.yaml
env: flex
runtime: python
entrypoint: gunicorn -b :$PORT main:app

runtime_config:
  python_version: 2
EOF

app2run list-incompatible-features
```

## Local development
```
# unit test
pip install pytest
py.test

# pylint
pip install pylint
pylint app2run

# Post for code review
git push origin HEAD:refs/for/main
```
