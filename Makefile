.PHONY : gen-py

gen-py:
	rm -rf ./fixture/gen-py
	thrift -r --gen py -o fixture fixture/thriftfiles/alice.thrift
python:
	python3 py/tfirht/simple.py ./fixture/gen-py/
