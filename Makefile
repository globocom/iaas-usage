.PHONY: clean pip test test-js run run-skip-test

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
	$(eval export ENV=app.config.TestConfig)
	@python -m unittest discover -p tests\.py

test-selenium: # run functional tests written for selenium engine
	$(eval export ENV=app.config.TestConfig)
	@python -m unittest discover -s app/functional_tests


test-js: #run javascript tests
	$(eval export ENV=app.config.TestConfig)
	@jasmine-ci


run: # run local server at 8080
	@python manage.py runserver

