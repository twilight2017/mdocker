class Dockerfile:
    Dockerfile_PDM = """
    FROM python:3.9 as builder

    ARG ssh_prv_key

    # Authorize SSH Host
    RUN mkdir -p /root/.ssh && \
        chmod 0700 /root/.ssh && \
        ssh-keyscan gitee.com > /root/.ssh/known_hosts

    # Add the keys and set permissions
    RUN echo "${ssh_prv_key}" > /root/.ssh/id_ed25519 && \
        chmod 600 /root/.ssh/id_ed25519

    # install PDM
    RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install -U setuptools wheel pip
    RUN pip install pdm

    # copy files
    COPY pyproject.toml pdm.lock README.md /project/

    # install dependencies and project
    WORKDIR /project
    RUN pdm install --prod --no-lock --no-editable


    # base image
    FROM python:3.9

    # retrieve packages from build stage
    ENV PYTHONPATH=/project/pkgs
    COPY --from=builder /project/__pypackages__/3.9/lib /project/pkgs
    COPY . /project/src

    # set command/entrypoint, adapt to fit your needs
    WORKDIR /project/src
    CMD ["/project/src/entrypoint.sh"]
    """