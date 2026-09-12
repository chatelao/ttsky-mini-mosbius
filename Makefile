# Top-level Makefile for Mini-MOSbius

all:
	$(MAKE) -C src all

check:
	$(MAKE) -C src check

lint:
	$(MAKE) -C src lint

clean:
	$(MAKE) -C src clean

.PHONY: all check lint clean
