.PHONY: init sync upgrade models test publish clean

py_version := 3.10
python := venv/bin/python

# -------------------------------------------------------- Dependency management {{{1

upgrade_tools := $(python) -m pip install --upgrade --upgrade-strategy=eager pip pip-tools
init:
	python$(py_version) -m venv venv
	$(upgrade_tools)

# --build-isolation is the default; --resolver=backtracking will become the default in
# v7.0.0
pip_compile := $(python) -m piptools compile --extra=dev --resolver=backtracking \
               --emit-options --generate-hashes --allow-unsafe --output-file
requirements_in := pyproject.toml self-editable.txt
requirements.txt: $(requirements_in)
	$(pip_compile) $@ $^

pip_sync := $(python) -m piptools sync requirements.txt
sync: requirements.txt
	$(pip_sync)

upgrade: requirements.txt
	$(upgrade_tools)
	$(pip_compile) $< --upgrade $(requirements_in)
	$(pip_sync)

# ---------------------------------------------------------------------- Testing {{{1

udpipe_model := czech-pdt-ud-2.4-190531.udpipe
$(udpipe_model):
	curl --silent --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-2998/$(udpipe_model)

morphodita := czech-morfflex-pdt-161115
morphodita_zip := $(morphodita).zip
morphodita_tagger := $(morphodita).tagger
$(morphodita_tagger):
	curl --silent --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1836/$(morphodita_zip)
	unzip -q $(morphodita_zip)
	mv $(morphodita)/$(morphodita_tagger) .
	rm -rf $(morphodita) $(morphodita_zip)

models: $(udpipe_model) $(morphodita_tagger)

test:
	$(python) -m pytest
	@echo 'TIP: To investigate errors in test cases, re-run pytest with --log-level DEBUG.'

# ------------------------------------------------------------------- Publishing {{{1

dist: pyproject.toml src
	$(python) -m build
	$(python) -m twine check dist/*

publish:
	$(python) -m twine upload --repository corpy dist/*

clean:
	rm -rf dist
	find src -ignore_readdir_race -path *.egg-info* -delete
