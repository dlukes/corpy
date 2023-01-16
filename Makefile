.PHONY: init sync upgrade models test publish clean

py_version := 3.10
python := venv/bin/python

# -------------------------------------------------------- Dependency management {{{1

# Can also use define ... endef here for "canned recipes", see:
# https://www.gnu.org/software/make/manual/html_node/Canned-Recipes.html
upgrade_tools := $(python) -m pip install --upgrade --upgrade-strategy=eager pip pip-tools
init:
	python$(py_version) -m venv venv
	$(upgrade_tools)

requirements_in := pyproject.toml self-editable.in
# --build-isolation is the default; --resolver=backtracking will become the
# default in v7.0.0. Getting editable installs with relative paths is a bit
# workaroundy right now, see https://github.com/jazzband/pip-tools/issues/204.
# Also, you should really have a separate requirements.txt for each OS / Python
# version etc. That's too much work right now for something that's essentially
# just a best effort attempt to replicate your last working dev env. but see:
# https://github.com/jazzband/pip-tools#cross-environment-usage-of-requirementsinrequirementstxt-and-pip-compile
pip_compile := $(python) -m piptools compile --extra=dev --resolver=backtracking \
               --emit-options --generate-hashes --allow-unsafe \
               --output-file requirements.txt $(requirements_in)
requirements.txt: $(requirements_in)
	$(pip_compile)

pip_sync := $(python) -m piptools sync requirements.txt
sync:
	$(pip_sync)

upgrade:
	$(upgrade_tools)
	$(pip_compile) --upgrade
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
	$(python) -m twine upload dist/*

clean:
	rm -rf dist
	find src -ignore_readdir_race -path *.egg-info* -delete
