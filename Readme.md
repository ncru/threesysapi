
# 3Sys DM Steg API

**An Application Programming Interface for the Validation of Digital Documents Using Data Matrix Image Steganography**

A Computer Science Research Project developed by **3Sys**, comprised of:

- Don Franco Ramos
- Geezan Loi Esteron
- Kent Nicholson Cruda


------------


## Overview

This API was developed in the interest of preserving document validity. It does so by using a two dimensional barcode, called 'Data Matrix' as an electronic document signature.

By incorporating Image Steganography into a Data Matrix image, we can obscure another message inside, aside from the encoded message of the Data Matrix.

This 'steganographized' Data Matrix image is then used in an electronic document as a digital signature.

Both copies of the signed and unsigned document are recorded in a database (this project uses [PostgreSQL](https://www.postgresql.org/) as database). These records are used for the API's verification of signed documents.

## Working Demo
A demo web application has been created in order to present the capabilities of this API, accessible through this [link](https://threesysapidemo.up.railway.app/).


## Features
- Signing PDF documents using a 'Steganographized' Data Matrix code as a signature
- Verifying validity of signed PDFs by the API

## Requirements:
* Python 3.7+
* [Flask](https://pypi.org/project/flask/)
* [gunicorn](https://pypi.org/project/gunicorn/)
* [dotenv](https://pypi.org/project/dotenv/) - for loading environment variables
* [PyMuPDF](https://pypi.org/project/PyMuPDF/) - for reading PDFs
* [Pillow](https://pypi.org/project/Pillow/) - for image manipulation
* [pylibdmtx](https://pypi.org/project/pylibdmtx/) - for Data Matrix code reading
* [Treepoem](https://pypi.org/project/treepoem/) - for 'Steganographized' Data Matrix code creation
* [psycopg2](https://pypi.org/project/psycopg/) - a Python adapter for PostgreSQL

Other requirements (shared libraries required by some modules; for Docker deployment/ other OS environments):
* [ghostscript](https://ghostscript.com/releases/gsdnld.html)- required by Treepoem
* [libdmtx0a](https://packages.ubuntu.com/kinetic/libdmtx0b) ([alternative link](https://github.com/dmtx/libdmtx)) - required by pylibdmtx

All of the aforementioned modules are listed in requirements.txt.

## Installation
To run this project locally, it is recommended to use a Python [virtual environment](https://docs.python.org/3/library/venv.html).

Clone this repository by downloading as a [zip archive](https://github.com/CodeDFranky/threesysapi/archive/refs/heads/master.zip), or through **cmd**:
```shell
git clone https://github.com/CodeDFranky/threesysapi
```

Install requirements using `pip`:
```shell
pip install -r requirements.txt
```
## Running the API
Navigate to the project directory, then using **cmd**:

```shell
python api.py
```

*OR*


If you have [Docker Desktop](https://www.docker.com/products/docker-desktop/), you can pull the latest image using **cmd**:

```shell
docker image pull ncru/threesysapi:latest
```
then run using :

```shell
docker run -p 5000:5000 -d threesysapi
```

This will run the API locally, accessible through http://127.0.0.1:5000/ (you can change the port number on any available port if 5000 is occupied).

On successful run, the default route of the API will be shown in the browser, with the message:
```javascript
{
	"message" : "Please use /generate or /verify to utilize this API or open this demo application: https://threesysapidemo.up.railway.app/"
}
```
## Interaction
To interact with the two API endpoints, `/generate` and `/verify`, a front end web application may be of use. Alternatively, you can use API tools like [Postman](https://www.postman.com/).

The API receives `multipart/form-data` for requests, containing these key-value pairs:

##### /generate
- **file** - a PDF file.
- **location** - text indicating which position should the signature be placed (top-left/top-right/bottom-left/bottom-right).

##### /verify
- **file** - a PDF file.

------------


&copy; 3Sys, 2022