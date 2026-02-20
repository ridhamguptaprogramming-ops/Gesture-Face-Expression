PYTHON ?= python3
CONFIG ?= config/mappings.json

.PHONY: install run test clean

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) run.py --config $(CONFIG)

test:
	PYTHONPYCACHEPREFIX=.pycache $(PYTHON) -m unittest discover -s tests -p "test_*.py" -q

clean:
	rm -rf .pycache __pycache__ captures
