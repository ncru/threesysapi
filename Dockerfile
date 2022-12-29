# syntax=docker/dockerfile:1

FROM python:3.11-slim-bullseye

RUN apt-get update \
    && apt-get install -y libdmtx0b \
    && apt-get install -y ghostscript

# copy the requirements file into the image
COPY ./requirements.txt /threesysapi/requirements.txt

# switch working directory
WORKDIR /threesysapi

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /threesysapi

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["api.py"]