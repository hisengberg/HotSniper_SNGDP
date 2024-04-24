SCRIPTS_DIR:=$(dir $(realpath $(lastword $(MAKEFILE_LIST))))
TOOLS_DIR:=$(dir $(SCRIPTS_DIR:%/=%))
export BENCHMARKS_ROOT:=$(shell "$(TOOLS_DIR)/python/env_setup_bm.py" --benchmarks)
export SNIPER_ROOT:=$(shell "$(TOOLS_DIR)/python/env_setup_bm.py" --sniper)
export GRAPHITE_ROOT:=$(SNIPER_ROOT)
