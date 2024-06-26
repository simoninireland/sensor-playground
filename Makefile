# Makefile for sensor playground experiment
#
# Copyright (C) 2024 Simon Dobson
#
# This file is part of sensor-playground, an experimental framework for
# target counting and higher-order sensor data analytics
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/gpl.html>.

# ----- Sources -----

# Notebooks
NOTEBOOKS =  \
	introduction.ipynb \
	euler.ipynb

# Source code
SOURCES = \
	sensorplayground/__init__.py \
	sensorplayground/py.typed \
	sensorplayground/utils.py \
	sensorplayground/types.py \
	sensorplayground/position.py \
	sensorplayground/agent.py \
	sensorplayground/modalities.py \
	sensorplayground/playground.py \
	sensorplayground/sensor.py \
	sensorplayground/drawing.py \
	sensorplayground/euler.py

SOURCES_TESTS = \
	test/__init__.py \
	test/test_utils.py \
	test/test_euler.py \
	test/test_trajectory.py \
	test/test_playground.py \
	test/test_scenarios.py
TESTSUITE = test


# ----- Tools -----

# Root directory
ROOT = $(shell pwd)

# Base commands
PYTHON = python3
IPYTHON = ipython
JUPYTER = jupyter
PIP = pip
VIRTUALENV = $(PYTHON) -m venv
ACTIVATE = . $(VENV)/bin/activate
RSYNC = rsync
TR = tr
CAT = cat
SED = sed
GIT = git
RM = rm -fr
CP = cp
CHDIR = cd
MKDIR = mkdir -p
ZIP = zip -r
UNZIP = unzip
WGET = wget
ECHO = echo

# Datestamp
DATE = `date`

# Requirements and venv
VENV = venv3
REQUIREMENTS = requirements.txt
DEV_REQUIREMENTS = dev-requirements.txt
KNOWN_GOOD_REQUIREMENTS = known-good-requirements.txt

# Commands
RUN_SERVER = PYTHONPATH=. $(JUPYTER) notebook
RUN_TESTS = $(PYTHON) -m unittest discover


# ----- Top-level targets -----

# Default prints a help message
help:
	@make usage


# Run the notebook server
live: env
	$(ACTIVATE) && $(RUN_SERVER)

# Build a development venv
.PHONY: env
env: $(VENV)

$(VENV):
	$(VIRTUALENV) $(VENV)
	$(ACTIVATE) && $(PIP) install -U pip wheel
	$(ACTIVATE) && $(PIP) install -r $(REQUIREMENTS)
	$(ACTIVATE) && $(PIP) install -r $(DEV_REQUIREMENTS)


# Clean up the build
clean:

# Clean up everything, including the venv (which is expensive to rebuild)
reallyclean: clean
	$(RM) $(VENV)


# ----- Usage -----

define HELP_MESSAGE
Editing:
   make live         run the notebook server

Maintenance:
   make env          create a virtual environment
   make clean        clean-up the build (mainly the diagrams)
   make reallyclean  delete the venv and all the datasets as well

endef
export HELP_MESSAGE

usage:
	@echo "$$HELP_MESSAGE"
