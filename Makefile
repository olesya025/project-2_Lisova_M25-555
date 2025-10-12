install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	pipx install --force dist/*.whl

lint:
	poetry run ruff check .

.PHONY: install project build publish package-install lint