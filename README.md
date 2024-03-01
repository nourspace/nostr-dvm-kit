# Nostr-DVM-Kit

Tools for building Nostr DVMs.

## Resources

- https://github.com/sloria/environs

- https://typer.tiangolo.com
- https://docs.pydantic.dev
- https://www.structlog.org


## Setup

```shell
poetry install
poetry shell
python cli.py dvm_echo.Echo
```

## Docker

```shell

docker buildx build --platform linux/amd64 -t nourspace/dvm-kit --load .

docker run --rm -it --platform linux/amd64 nourspace/dvm-kit bash
```
