# Hostname generator microservice
# dbv/2018-09-27
# built: docker build .
# run: docker run -i -p 5000:5000 -v /local/dir:/data -e HOSTGEN_DATADIR=/data -e HOSTGEN_PATTERN='dbv%i' -e HOSTGEN_START=4 -e HOSTGEN_DIGITS=6 <build-id>

# Base image
FROM fedora:25

LABEL vendor="Daniel Buøy-Vehn"
LABEL Description="Image for hostname generation using REST"
LABEL hostgen.release-date="2018-09-27"
LABEL hostgen.version="1.0.0"

ENV HOSTGEN_DATADIR='/data'
ENV HOSTGEN_DIGITS=3
ENV HOSTGEN_LISTENIP='0.0.0.0'
ENV HOSTGEN_LISTENPORT='5000'
ENV HOSTGEN_PATTERN='host%i'
ENV HOSTGEN_RANDOM_LENGTH=8
ENV HOSTGEN_START=1

# Add author
MAINTAINER Daniel Buøy-Vehn

# Copy the script
COPY hostgen.py /root/bin/hostgen.py

# Install requirements
RUN dnf install -y python-pip; yum clean all; /usr/bin/pip install --upgrade pip; /usr/bin/pip install flask; chmod u+x /root/bin/hostgen.py; mkdir /data

# Predefined port
# can be overwritten with `docker run -p ...`
EXPOSE 5000/tcp

# Run command
CMD /root/bin/hostgen.py
