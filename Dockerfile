ADD file ... in /
CMD ["/bin/sh"]
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=C.UTF-8
ENV GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696D
ENV PYTHON_VERSION=3.10.9
ENV PYTHON_PIP_VERSION=22.3.1
ENV PYTHON_SETUPTOOLS_VERSION=65.5.1
ENV PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/1a96dc5acd0303c4700e02655aefd3bc68c78958/public/get-pip.py
ENV PYTHON_GET_PIP_SHA256=d1d09b0f9e745610657a528689ba3ea44a73bd19c60f4c954271b790c71c2653
CMD ["python3"]
RUN /bin/sh -c apk update
RUN /bin/sh -c cp /usr/share/zoneinfo/Europe/Andorra
RUN /bin/sh -c echo "Europe/Andorra"
RUN /bin/sh -c mkdir /scrapyrealestate/
ADD . /scrapyrealestate/ # buildkit
WORKDIR /scrapyrealestate/scrapyrealestate/
RUN /bin/sh -c pip install
RUN /bin/sh -c pip install
EXPOSE map[8080/tcp:{}]
CMD ["python" "./main.py"]
