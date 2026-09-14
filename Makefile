# Top-level Makefile for Mini-MOSbius

all:
	$(MAKE) -C src all

check:
	$(MAKE) -C src check

precheck:
	python3 py/run_precheck.py

lint:
	$(MAKE) -C src lint

clean:
	$(MAKE) -C src clean

.PHONY: all check precheck lint clean
