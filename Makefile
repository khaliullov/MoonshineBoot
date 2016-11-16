mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir  := $(dir $(mkfile_path))

.PHONY: all clean status test deploy update

all:
	@echo "make test - perform unit tests"
        @echo "make venv - create virtualenv (atomatically called with other tasks if needed)"
        @echo "make clean - remove virtualenv"
	@echo "make status - get current status of deploy in AWS"	
	@echo "make deploy - deploy to AWS"	
	@echo "make update - update deployed project in AWS (apply new changes)"	
	@echo "make test - run unit test, covetage test, etc."	

venv:
	virtualenv $(mkfile_dir)venv
	$(mkfile_dir)venv/bin/pip install -r $(mkfile_dir)requirements.txt

clean:
	rm -rf $(mkfile_dir)venv

status: venv
	. $(mkfile_dir)venv/bin/activate; \
	$(mkfile_dir)venv/bin/zappa status

deploy: venv
	. $(mkfile_dir)venv/bin/activate; \
	$(mkfile_dir)venv/bin/zappa deploy production

update: venv
	. $(mkfile_dir)venv/bin/activate; \
	$(mkfile_dir)venv/bin/zappa update production

test: venv
	$(mkfile_dir)venv/bin/python manage.py test
