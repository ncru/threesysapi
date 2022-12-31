from flask import send_file, jsonify, make_response
import io
import base64


def default_route():
    response = jsonify(
        {
            "message": "Please use /generate or /verify to utilize this API or open this demo application <link>"
        }
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.status_code = 200
    return response


def input_fail(type):
    match type:
        case 0:
            response = jsonify({"message": "Invalid request"})
            response.status_code = 422
        case 1:
            response = jsonify({"message": "Pdf size unacceptable"})
            response.status_code = 422
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def generate_pass(TSdoc):
    if TSdoc.already_signed:
        return generate_fail()
    (new_pdf_data, new_pdf_file_name) = TSdoc.generate_dm_and_add_to_pdf()
    base64_str = base64.b64encode(new_pdf_data)
    response = jsonify({
        "signed-pdf-data": str(base64_str)
    })
    # response = make_response(send_file(
    #     io.BytesIO(new_pdf_data),
    #     mimetype="application/pdf",
    #     download_name=new_pdf_file_name,
    #     # as_attachment=True, auto download the file 'save as'
    # ))
    response.status_code = 200
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def generate_fail():
    response = jsonify(
        {"message": "The document has been previously signed by 3.Sys."})
    response.status_code = 422
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def generate_neutral():
    response = jsonify(
        {
            "message": "The document is already signed by 3.Sys. Document is possibly modified; use /verify to check if valid"
        }
    )
    response.status_code = 422
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def generate_fail_margin():
    response = jsonify(
        {
            "message": "The document must have clear space in the designated area for the signature"
        }
    )
    response.status_code = 400
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def verify_pass(TSdoc):
    response = jsonify(
        {
            "message": "This is a signed and valid document",
            "plain": TSdoc.regular_dm_payload,
        }
    )
    response.status_code = 200
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def verify_falsified():
    response = jsonify({"message": "This is a falsified document."})
    response.status_code = 422
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def verify_fail():
    response = jsonify(
        {"message": "This document has not gone through /generate"})
    response.status_code = 422
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def generate_if_hell(TSdoc):
    traits = TSdoc.traits
    # print(traits)
    print(list(traits.values()))
    # turn your dicts to a binary list, for free!
    traitsList = [int(x) for x in list(traits.values())]
    # fmt: off
    match (traitsList):
        case    [1, 0, 0, 0, 0] | \
                [1, 0, 0, 0, 1] | \
                [1, 0, 1, 0, 0] | \
                [1, 0, 1, 0, 1] | \
                [1, 1, 0, 0, 0] | \
                [1, 1, 1, 0, 0] | \
                [1, 1, 1, 0, 1] | \
                [1, 1, 0, 0, 1]:
            return generate_pass(TSdoc)
        case    [1, 0, 0, 1, 1] | \
                [1, 0, 1, 1, 0] | \
                [1, 0, 0, 1, 0] | \
                [1, 1, 0, 1, 0] | \
                [1, 1, 1, 1, 0] | \
                [1, 1, 1, 1, 1]: 
            return generate_fail()
        case    [1, 0, 1, 1, 1] | \
                [1, 1, 0, 1, 1]:
            return generate_neutral()
        case _:
            return generate_fail_margin()


# fmt: on


def verify_if_hell(TSdoc):
    traits = TSdoc.traits
    # print(traits)
    print(list(traits.values()))
    # turn your dicts to a binary list, for free!
    traitsList = [int(x) for x in list(traits.values())]
    # fmt: off
    match (traitsList):
        case    [1, 0, 1, 1, 0] | \
                [1, 0, 0, 1, 0] | \
                [1, 1, 0, 1, 0] | \
                [1, 1, 1, 1, 0]: 
            return verify_pass(TSdoc)

        case    [1, 0, 0, 1, 1] | \
                [1, 0, 1, 1, 1] | \
                [1, 1, 0, 1, 1] | \
                [1, 1, 1, 1, 1]:
            return verify_falsified()

        case    [1, 0, 0, 0, 0] | \
                [1, 0, 0, 0, 1] | \
                [1, 0, 1, 0, 0] | \
                [1, 0, 1, 0, 1] | \
                [1, 1, 0, 0, 0] | \
                [1, 1, 1, 0, 0] | \
                [1, 1, 1, 0, 1] | \
                [1, 1, 0, 0, 1]:
            return verify_fail()

        case _:
            return verify_fail()


# fmt: on
