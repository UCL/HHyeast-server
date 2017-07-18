FROM python

MAINTAINER ilectra "ilektra.christidi@ucl.ac.uk"

RUN git clone https://github.com/UCL/HHyeast-server.git

WORKDIR /HHyeast-server

RUN pip install -r requirements.txt

EXPOSE 5006

CMD bokeh serve lolliplotServer.py