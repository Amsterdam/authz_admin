.PHONY: test coverage

PYTHON = python3

test:
	$(PYTHON) setup.py test -a "-p no:cacheprovider --verbose --capture=no ."

coverage:
	$(PYTHON) setup.py test -a "-p no:cacheprovider --verbose --cov=oauth2 --cov-report=term --cov-config .coveragerc --capture=no ."
