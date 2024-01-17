
.PHONY: publish
publish:
	rm -rf dist
	poetry build
	poetry publish