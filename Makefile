build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	pipx install dist/*.whl

.PHONY: build publish package-install