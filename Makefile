JOBS ?= 4

.PHONY: pretty lint tests

pretty:
	black --target-version py38 --skip-string-normalization .
	isort --apply --recursive .
	unify --in-place --recursive .

lint:
	black --target-version py38 --check --skip-string-normalization .
	flake8 --jobs $(JOBS) --statistics .
	pylint --jobs $(JOBS) --rcfile=setup.cfg categorizer tests app.py

tests:
	pytest tests
