black:
    black dukto tests setup.py --check

flake:
    flake8 dukto tests setup.py

test:
    pytest

check: black flake test

install:
    python -m pip install -e .
