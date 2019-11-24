FROM python:3.7.4-slim
ENV DEBIAN_FRONTEND noninteractive

# docker build -t quay.io/vsoch/freegenes .

ARG ENABLE_LDAP=false
ARG ENABLE_PAM=false
ARG ENABLE_SAML=false

################################################################################
# CORE
# Do not modify this section

RUN apt-get update && apt-get install -y \
    cmake \
    git \
    libxmlsec1-dev \
    openssl \
    pkg-config \
    wget \
    vim

# Install Python requirements out of /tmp so not triggered if other contents of /code change
ADD requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

ADD . /code/

################################################################################
# PLUGINS
# You are free to uncomment the plugins that you want to use

# Install LDAP
RUN if $ENABLE_LDAP; then pip install python3-ldap ; fi;
RUN if $ENABLE_LDAP; then pip install django-auth-ldap ; fi;

# Install PAM Authentication
RUN if $ENABLE_PAM; then pip install django-pam ; fi;

# Install SAML
RUN if $ENABLE_SAML; then pip install python3-saml ; fi;
RUN if $ENABLE_SAML; then pip install social-auth-core[saml] ; fi;

################################################################################
# BASE

RUN mkdir -p /code && mkdir -p /code/data
RUN mkdir -p /var/www/data && chmod -R 0755 /code/data/

WORKDIR /code
RUN apt-get autoremove -y && \
    apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install crontab to run tasks - keep backup last 2 days, update tracking every 3 hours
RUN apt-get update && apt-get install -y cron
RUN echo "0 2 * * * python manage.py generate_mapdata /code/data/ordercoords.json" >> /code/cronjob
RUN echo "0 */3 * * * python manage.py update_tracking" >> /code/cronjob
RUN echo "0 1 * * * /bin/bash /code/scripts/backup_db.sh" >> /code/cronjob
RUN crontab /code/cronjob

CMD /code/docker/run_uwsgi.sh

EXPOSE 3031
