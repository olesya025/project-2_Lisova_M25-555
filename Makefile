install:
	poetry install

database:
	poetry run database

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	pipx install --force dist/*.whl

lint:
	poetry run ruff check .

.PHONY: install database build publish package-install lint