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

# --build-isolation is the default; --resolver=backtracking will become the
# default in v7.0.0. Getting editable installs with relative paths is a bit
# workaroundy right now, see https://github.com/jazzband/pip-tools/issues/204.
# Also, you should really have a separate requirements.txt for each OS / Python
# version etc. That's too much work right now for something that's essentially
# just a best effort attempt to replicate your last working dev env. but see:
# https://github.com/jazzband/pip-tools#cross-environment-usage-of-requirementsinrequirementstxt-and-pip-compile
pip_compile := $(python) -m piptools compile --extra=dev --resolver=backtracking \
               --emit-options --generate-hashes --allow-unsafe \
               --output-file requirements.txt pyproject.toml
requirements.txt: pyproject.toml
	$(pip_compile)

pip_sync := $(python) -m piptools sync requirements.txt && \
            $(python) -m pip install --no-deps --editable .
sync:
	$(pip_sync)

upgrade:
	$(upgrade_tools)
	$(pip_compile) --upgrade
	$(pip_sync)

# ---------------------------------------------------------------------- Testing {{{1

lindat := https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle

udpipe_handle := 11234/1-3131
udpipe_model := czech-pdt-ud-2.5-191206.udpipe
$(udpipe_model):
	curl --remote-name-all $(lindat)/$(udpipe_handle)/$(udpipe_model)
	ln -s $(udpipe_model) czech-pdt-ud.udpipe

morphodita_handle := 11234/1-4794
morphodita := czech-morfflex2.0-pdtc1.0-220710
morphodita_zip := $(morphodita).zip
morphodita_tagger := $(morphodita).tagger
$(morphodita_tagger):
	curl --remote-name-all $(lindat)/$(morphodita_handle)/$(morphodita_zip)
	unzip -q $(morphodita_zip)
	mv $(morphodita)/$(morphodita_tagger) .
	rm -rf $(morphodita) $(morphodita_zip)
	ln -s $(morphodita_tagger) czech-morfflex-pdt.tagger

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
