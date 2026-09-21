# Contributing

Install the pinned dependencies with `python -m pip install -e .` from this
directory. `requirements.txt` remains the exact direct runtime compatibility
pin set for environments that do not install the package. Run the offline
checks before submitting a change:

```bash
python -m unittest discover -s tests -v
python -m compileall -q src
python -m pip wheel --no-deps --no-build-isolation -w /tmp/visitkorea-dist .
```

Do not add live API calls or credentials to tests.
