.PHONY: clean pip test test-selenium test-js run run-skip-test

default:
	@awk -F\: '/^[a-z_]+:/ && !/default/ {printf "- %-20s %s\n", $$1, $$2}' Makefile


clean: # remove temporary files
	@find . -name \*.pyc -delete
	@find . -name \*.orig -delete
	@find . -name \*.bak -delete
	@find . -name __pycache__ -delete
	@find . -name coverage.xml -delete
	@find . -name test-report.xml -delete
	@find . -name .coverage -delete


pip: # install pip libraries
	@pip install -r requirements.txt


compile: # compile to check syntax
	@find . -name "*.py" -exec python -m py_compile {} +


test: # run tests
	@python -m unittest discover -p tests\.py

test-selenium: # run functional tests written for selenium engine
	@python -m unittest discover -s app/functional_tests


test-js: #run javascript tests
	@jasmine-ci


run-skip-test: # run local server skipping test
	@python run.py


run: # run local server at 8080 after running tests
	@jasmine-ci
	@python run.py

