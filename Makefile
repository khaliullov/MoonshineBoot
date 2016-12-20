mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir  := $(dir $(mkfile_path))

.PHONY: all clean status test deploy update run tail

all:
	@echo "make test - perform unit test, covetage test, etc."	
	@echo "make venv - create virtualenv (atomatically called with other tasks if needed)"
	@echo "make clean - remove virtualenv"
	@echo "make status - get current status of deploy in AWS"	
	@echo "make deploy - deploy to AWS"	
	@echo "make tail - tail AWS CloudWatch logs"
	@echo "make update - update deployed project in AWS (apply new changes)"	
	@echo "make run - run local server for manual testing on 0.0.0.0:8000"	

venv:
	virtualenv $(mkfile_dir)venv
	$(mkfile_dir)venv/bin/pip install -r $(mkfile_dir)requirements.txt

clean:
	rm -rf $(mkfile_dir)venv

status deploy update tail: venv
	. $(mkfile_dir)venv/bin/activate; \
	$(mkfile_dir)venv/bin/zappa $@ production

test: venv
	$(mkfile_dir)venv/bin/python manage.py test

run: venv
	$(mkfile_dir)venv/bin/python manage.py runserver 0.0.0.0:8000
