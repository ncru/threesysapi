# syntax=docker/dockerfile:1

FROM python:3.11-slim-bullseye

RUN apt-get update \
    && apt-get install -y libdmtx0b

# copy the requirements file into the image
COPY ./requirements.txt /benchpress/requirements.txt

# switch working directory
WORKDIR /benchpress

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /benchpress

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["test.py"]