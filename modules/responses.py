from flask import send_file, jsonify, make_response
import io


def default_route():
    response = jsonify(
        {
            "message": "Please use /generate or /verify to utilize this API or open this demo application: https://threesysapidemo.up.railway.app/"
        }
    )
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

    return response


def generate_pass(TSdoc):
    if TSdoc.already_signed:
        return generate_fail()
    (new_pdf_data, new_pdf_file_name) = TSdoc.generate_dm_and_add_to_pdf()
    response = make_response(
        send_file(
            io.BytesIO(new_pdf_data),
            mimetype="application/pdf",
            download_name=new_pdf_file_name,
        )
    )
    response.status_code = 200

    return response


def generate_fail():
    response = jsonify({"message": "The document has been previously signed by 3.Sys."})
    response.status_code = 422

    return response


def generate_neutral():
    response = jsonify(
        {
            "message": "The document is already signed by 3.Sys. Document is possibly modified; use /verify to check if valid"
        }
    )
    response.status_code = 422

    return response


def generate_fail_margin():
    response = jsonify(
        {
            "message": "The document must have clear space in the designated area for the signature"
        }
    )
    response.status_code = 400

    return response


def verify_pass(TSdoc):
    response = jsonify(
        {
            "message": "This is a signed and valid document",
            "plain": TSdoc.regular_dm_payload,
        }
    )
    response.status_code = 200

    return response


def verify_falsified():
    response = jsonify({"message": "This is a falsified document."})
    response.status_code = 422

    return response


def verify_fail():
    response = jsonify({"message": "This document has not gone through /generate"})
    response.status_code = 422

    return response


def generate_decision(TSdoc):
    traits = TSdoc.traits
    # print(traits)
    print(list(traits.values()))
    # convert dictionary to a binary list
    traitsList = [int(x) for x in list(traits.values())]
    # fmt: off
    match (traitsList):
        case [1, 0, 0, 0, 0] |\
             [1, 0, 0, 0, 1] |\
             [1, 0, 1, 0, 0] |\
             [1, 0, 1, 0, 1] |\
             [1, 1, 0, 0, 0] |\
             [1, 1, 1, 0, 0] |\
             [1, 1, 1, 0, 1] |\
             [1, 1, 0, 0, 1]:
            return generate_pass(TSdoc)
        case [1, 0, 0, 1, 1] |\
             [1, 0, 1, 1, 0] |\
             [1, 0, 0, 1, 0] |\
             [1, 1, 0, 1, 0] |\
             [1, 1, 1, 1, 0] |\
             [1, 1, 1, 1, 1]:
            return generate_fail()
        case [0, 1, 1, 1, 0] |\
             [0, 1, 1, 1, 1] |\
             [1, 0, 1, 1, 1] |\
             [1, 1, 0, 1, 1]:
            return generate_neutral()
        case _:
            return generate_fail_margin()


# fmt:on
# fmt: off
def verify_decision(TSdoc):
    traits = TSdoc.traits
    # print(traits)
    print(list(traits.values()))
    # convert dictionary to a binary list
    traitsList = [int(x) for x in list(traits.values())]

    match (traitsList):
        case [1, 0, 1, 1, 0] |\
             [1, 0, 0, 1, 0] |\
             [1, 1, 0, 1, 0] |\
             [1, 1, 1, 1, 0]:
            return verify_pass(TSdoc)

        case [1, 0, 0, 1, 1] |\
             [1, 0, 1, 1, 1] |\
             [1, 1, 0, 1, 1] |\
             [1, 1, 1, 1, 1]:
            return verify_falsified()

        case [1, 0, 0, 0, 0] |\
             [1, 0, 0, 0, 1] |\
             [1, 0, 1, 0, 0] |\
             [1, 0, 1, 0, 1] |\
             [1, 1, 0, 0, 0] |\
             [1, 1, 1, 0, 0] |\
             [1, 1, 1, 0, 1] |\
             [1, 1, 0, 0, 1]:
            return verify_fail()

        case _:
            return verify_fail()
# fmt:on
