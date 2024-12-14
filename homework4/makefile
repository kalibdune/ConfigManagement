.PHONY: run

run:
	python3 assembler.py program.txt out.bin log.yaml
	python3 interpreter.py out.bin res.yaml 0 $(or $(N), 20)