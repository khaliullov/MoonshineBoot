mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir  := $(dir $(mkfile_path))

.PHONY: all test deploy

all:
	@echo "make test - perform unit tests"
	@echo "make deploy - deploy to AWS"	

venv:
	virtualenv $(mkfile_dir)venv
	$(mkfile_dir)venv/bin/pip install -r $(mkfile_dir)requirements.txt

clean:
	rm -rf $(mkfile_dir)venv

deploy: venv
	. $(mkfile_dir)venv/bin/activate; \
	$(mkfile_dir)venv/bin/zappa deploy production

update: venv
	. $(mkfile_dir)venv/bin/activate; \
	$(mkfile_dir)venv/bin/zappa update production

test: venv
	$(mkfile_dir)venv/bin/python manage.py test
