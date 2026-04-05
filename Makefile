PYTHON ?= python

.PHONY: build run test clean update-baseline

build:
	mkdir -p workloads/bin
	cc -O2 -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra workloads/matrix_multiply.c -o workloads/bin/matrix_multiply
	cc -O2 -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra workloads/memory_bandwidth.c -o workloads/bin/memory_bandwidth
	cc -O2 -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra workloads/vector_add.c -o workloads/bin/vector_add

run:
	PYTHONPATH=. $(PYTHON) -m harness.runner --config-dir configs --bin-dir workloads/bin --baseline baselines/baseline.json --report-dir reports/latest

test:
	PYTHONPATH=. pytest -q

update-baseline:
	PYTHONPATH=. $(PYTHON) -m harness.runner --config-dir configs --bin-dir workloads/bin --baseline baselines/baseline.json --report-dir reports/latest --update-baseline

clean:
	rm -rf workloads/bin reports/latest/*
