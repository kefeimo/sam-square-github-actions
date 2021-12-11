install:
	pip install --upgrade pip && \
	pip install -r squareup_api/requirements.txt && \
	pip install -e squareup_api/
	
		# pip install -r squareup/requirements.txt &&\
		# pip install -r tests/requirements.txt

test:  # require environment variable SQUARE_TOKEN_TEST='XXXX', ex: SQUARE_TOKEN_TEST='XXXX' make test
	# python -m pytest -vv test_hello.py
	# python -m pytest -vv test_hello_2.py
	SQUARE_TOKEN_TEST=$(SQUARE_TOKEN_TEST) python -m pytest -vv squareup_api/tests/test_*.py
	
	
test_occ:  # occationally test. require environment variable SQUARE_TOKEN_TEST='XXXX', ex: SQUARE_TOKEN_TEST='XXXX' make test_occ
	SQUARE_TOKEN_TEST=$(SQUARE_TOKEN_TEST) python -m pytest -vv squareup_api/tests/occational_test_square_utils_catalog.py

format:
	black *.py


lint:
	pylint --disable=R,C squareup/*.py

all: install lint test 


test_all: test test_occ