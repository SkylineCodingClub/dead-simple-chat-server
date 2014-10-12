default: tests

clean:
	rm -f $(shell find . -name "*.pyc")

tests:
	python chat/server 127.0.0.1 10000 &
	python -m nose --process-timeout=5 --with-coverage --cover-package chat
	kill -9 `lsof -t -i:10000`

test_watcher:
	watch python -m nose

style_check:
	python -m pep8 $(shell find . -name "*.py")

style_watcher:
	watch python -m pep8 $(shell find . -name "*.py")

lint_check:
	python -m pylint --report=n $(shell find . -name "*.py")
