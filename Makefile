
.PHONY: publish
publish:
	rm -rf dist
	poetry build
	poetry publish

.PHONY: test
test:
	poetry run pytest -v