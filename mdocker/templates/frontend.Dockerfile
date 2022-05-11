FROM python:3.9 as base_stage1

ARG ssh_prv_key

# Authorize SSH Host
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan gitee.com > /root/.ssh/known_hosts

# Add the keys and set permissions
RUN echo "${ssh_prv_key}" > /root/.ssh/id_ed25519 && \
    chmod 600 /root/.ssh/id_ed25519

# install poetry
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install -U setuptools wheel pip
RUN pip install poetry

COPY ../dockerfiles /project
WORKDIR /project

RUN poetry install --no-dev --no-interaction --no-ansi


FROM base_stage1 as base_stage2

# install poetry
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu/cn/simple && pip install -U setuptools wheel pip
RUN pip install poetry

# now we have all the files needed
COPY --from=base_satge1 /project /project

# set command/entrypoint, adapt to fit your needs
WORKDIR /project
CMD ['/project/entrypoint.sh']