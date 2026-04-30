help:
  @just -l


[group('Initialize')]
init:
  @uv venv

[group('Run App')]
up:
  @uv run src/main.py

clean-python:
  @rm -rf ./.venv
  @echo "\`.venv\` folder is deleted."