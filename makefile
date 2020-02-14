.PHONY: init test lint pretty precommit_install bump_major bump_minor bump_patch

BIN = poetry run
CODE = listful

init:
	python3 -m venv .venv
	poetry install

test:
	$(BIN) pytest --verbosity=2 --showlocals --strict --log-level=DEBUG --cov=$(CODE) $(args)
	$(BIN) byexample -l python README.md

testreport:
	$(BIN) pytest --verbosity=2 --showlocals --strict --log-level=DEBUG --cov=$(CODE) --cov-report=html $(args)

lint:
	$(BIN) flake8 --jobs 4 --statistics --show-source --radon-max-cc 10 $(CODE) tests
	$(BIN) pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	$(BIN) mypy $(CODE) tests
	$(BIN) black --target-version py37 --skip-string-normalization --line-length=79 --check $(CODE) tests
	$(BIN) pytest --dead-fixtures --dup-fixtures

pretty:
	$(BIN) isort --apply --recursive $(CODE) tests
	$(BIN) black --target-version py37 --skip-string-normalization --line-length=79 $(CODE) tests
	$(BIN) unify --in-place --recursive $(CODE) tests

precommit_install:
	echo '#!/bin/sh\nmake lint test\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

bump_major:
	$(BIN) bumpversion major

bump_minor:
	$(BIN) bumpversion minor

bump_patch:
	$(BIN) bumpversion patch
