
FROM ubuntu

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "python-software-properties"]
RUN ["add-apt-repository", "ppa:fkrull/deadsnakes"]
RUN ["add-apt-repository", "ppa:pypy"]
RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "pypy", "python2.6", "python2.6-dev", "python3.3", "python3.3-dev", "python2.7", "python2.7-dev"]
RUN ["apt-get", "install", "-y", "python-pip"]
RUN ["pip", "install", "tox==1.6.1", "coverage"]

WORKDIR /pywizard

ENV PYTHONDONTWRITEBYTECODE 1
ENV TOX_DOCKER 1
ENV TOX_DISTRO ubuntu