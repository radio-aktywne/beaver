ARG MINIO_CLIENT_IMAGE_TAG=RELEASE.2022-03-17T20-25-06Z
ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM minio/mc:$MINIO_CLIENT_IMAGE_TAG AS mc

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG AS base

COPY --from=mc /usr/bin/mc /usr/bin/mc

# add bash, because it's not available by default on alpine
# and ffmpeg because we need it for streaming
# and ca-certificates for mc
# and git to get pystreams
RUN apk add --no-cache bash ffmpeg ca-certificates git

WORKDIR /app/

# install poetry
COPY ./requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install -r ./requirements.txt

# create new environment
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yaml ./environment.yaml
RUN --mount=type=cache,target=/opt/conda/pkgs \
    conda env create -f ./environment.yaml

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "emishows", "/bin/bash", "-c"]

WORKDIR /app/emishows/

# add poetry files
COPY ./emishows/pyproject.toml ./emishows/poetry.lock ./

FROM base AS test

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main,test

# add source, tests and necessary files
COPY ./emishows/src/ ./src/
COPY ./emishows/tests/ ./tests/
COPY ./emishows/LICENSE ./emishows/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emishows

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh", "pytest"]
CMD []

FROM base AS production

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main

# add source and necessary files
COPY ./emishows/src/ ./src/
COPY ./emishows/LICENSE ./emishows/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emishows

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENV EMISHOWS_HOST=0.0.0.0 \
    EMISHOWS_PORT=35000 \
    EMISHOWS_CERTS_DIR=/etc/certs \
    EMISHOWS_DB__HOST=localhost \
    EMISHOWS_DB__PORT=34000 \
    EMISHOWS_DB__PASSWORD=password \
    EMISHOWS_EMITIMES__HOST=localhost \
    EMISHOWS_EMITIMES__PORT=36000 \
    EMISHOWS_EMITIMES__USER=user \
    EMISHOWS_EMITIMES__PASSWORD=password \
    EMISHOWS_EMITIMES__CALENDAR=emitimes

EXPOSE 35000

ENTRYPOINT ["./entrypoint.sh", "emishows"]
CMD []
