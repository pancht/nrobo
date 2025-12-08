# Freeze requirements

`pip freeze > requirements.txt`

# Setup local development environment

`pip install -e .`

Then do

`which nrobo`

# Clear pytest cache

``pytest --cache-clear
``


`python -m flake8 --config=configs/.flake8 src/nrobo`
`pre-commit run --all-files`

Recreate venv

```bash
# From your project root
rm -rf .venv
# or whatever your venv folder is called
python -m venv .venv
source .venv/bin/activate # or .venv\Scripts\activate on Windows
```


# installation from test.pypi
`pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple nrobo==2025.5.2`
