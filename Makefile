clean:
	find . -name "*.pyc" -exec rm {} \;

documentation:
	sphinx-build -E sphinx-docs/ docs/html/

test: clean
	pytest --cov-config .coveragerc \
		--cov=map_maker \
		tests/

lint:
	flake8 map_maker/
	flake8 tests/
