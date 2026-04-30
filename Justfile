help:
  @just -l


[group('Initialize')]
init:
  @uv venv

[group('Run App')]
up:
  @uv run src/main.py

[group('Test')]
test:
  @uv run pytest src/

clean-python:
  @rm -rf ./.venv
  @echo "\`.venv\` folder is deleted."