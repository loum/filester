.SILENT:
.DEFAULT_GOAL := help

MAKESTER__STANDALONE := true
MAKESTER__INCLUDES := py docker versioning docs
MAKESTER__VENV_HOME := $(PWD)/.venv

include $(HOME)/.makester/makefiles/makester.mk

#
# Makester overrides.
#
MAKESTER__GITVERSION_CONFIG := GitVersion.yml
MAKESTER__VERSION_FILE := $(MAKESTER__PYTHON_PROJECT_ROOT)/VERSION
MAKESTER__GITVERSION_VERSION := 6.1.0-alpine.3.20-8.0

#
# Local Makefile targets.
#
_venv-init: py-venv-clear py-venv-init

# Build the local development environment.
init-dev: _venv-init
	MAKESTER__PIP_INSTALL_EXTRAS=dev $(MAKE) py-install-extras

# Streamlined production packages.
init: _venv-init
	$(MAKE) py-install

# Dagsesh test harness.
#
TESTS_TO_RUN := $(if $(TESTS),$(TESTS),tests)
PRIME_TEST_CONTEXT ?= true
ifneq (tests,$(TESTS_TO_RUN))
COVERAGE := -no-cov
endif

tests:
	$(MAKESTER__PYTHON) -m pytest $(TESTS_TO_RUN) $(COVERAGE)

help: makester-help
	printf "\n(Makefile)\n"
	$(call help-line,init,Build the local Python-based virtual environment)
	$(call help-line,init-dev,Build the local Python-based virtual environment with dev tools)
	$(call help-line,tests,Run code test suite)

.PHONY: help tests docs
