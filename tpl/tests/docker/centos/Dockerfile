
FROM centos

RUN wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
RUN wget http://rpms.famillecollet.com/enterprise/remi-release-6.rpm
RUN rpm -Uvh remi-release-6*.rpm epel-release-6*.rpm

RUN yum -y --enablerepo=remi install python-pip

RUN pip-python install tox

WORKDIR /pywizard

ENV PYTHONDONTWRITEBYTECODE 1
ENV TOX_DOCKER 1
ENV TOX_DISTRO centos