.PHONY: install test

PACKAGE := fitbit

install:
	pip install -r requirements.txt

test:
	python setup.py --version
	pytest -v --cov=$(PACKAGE) --cov-report html:cover --cov-report term-missing
