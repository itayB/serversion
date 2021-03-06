MODULE := serversion

BLUE=\033[0;34m
NC=\033[0m # No Color

.PHONY: lint test type

run:
	@python -m $(MODULE)

test:
	@py.test -o junit_family=xunit2 --junitxml result.xml -v --ff --cov=${MODULE} --cov-report=xml --cov-report=term tests

lint:
	@echo "\n${BLUE}Running Pylint against source and test files...${NC}\n"
	@pylint --rcfile=setup.cfg **/*.py
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@flake8
	@echo "\n${BLUE}Running Bandit against source files...${NC}\n"
	@bandit -r --ini setup.cfg

type:
	@mypy ${MODULE}

all: lint type test
