# bash is needed to run pushd/popd for the analyzers target
SHELL:=/bin/bash

help:
	@printf "Available targets: check, analyzers, clean\n\n"

check:
	coverage run --omit="lib/*","setup.py","kiskadee/tests/*",".eggs/*",".venv/*","/usr/*" -m unittest kiskadee/tests/*/*.py
	coverage html

check_units:
	python3 -m unittest kiskadee/tests/units/*.py

check_integration:
	python3 -m unittest kiskadee/tests/integration/*.py

check_api:
	python3 -m unittest kiskadee/tests/api/*.py

check_plugins:
	python3 -m unittest kiskadee/tests/plugins/*.py

analyzers:
	docker ps 2> /dev/null; \
	if [ $$? -ne 1 ]; then \
			echo "docker daemon properly configured. Building images..."; \
	else \
			echo "docker daemon was not properly configured, is the service running?"; \
			exit; \
	fi; \
	pushd util/dockerfiles; \
	for analyzer in `ls`; do \
		pushd $$analyzer; \
		docker build . -t $$analyzer; \
		popd; \
	done

deploy:
	echo "Installing kiskadee...";
	ansible-playbook -i playbook/${INVENTORY} playbook/site.yml -f 10;

clean:
	rm -rf htmlcov .coverage kiskadee.egg-info build dist
