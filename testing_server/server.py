import json
from flask import Flask, request, jsonify, Response
import xml.etree.ElementTree as ET
from datetime import datetime

app = Flask(__name__)

def round_to_two_decimals(value):
    return round(float(value), 2)

def load_positions():
    try:
        with open('positions.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {
            "balances": {},
            "transactions": {}
        }

    if 'balances' not in data:
        data['balances'] = {}
    if 'transactions' not in data:
        data['transactions'] = {}

    return data

def save_positions(data):
    with open('positions.json', 'w') as file:
        json.dump(data, file, indent=4)

def clear_old_positions():
    data = load_positions()
    today = datetime.today().strftime('%Y-%m-%d')

    for currency, transactions in data['transactions'].items():
        if today in transactions:
            data['transactions'][currency] = {today: transactions[today]}

    save_positions(data)

def parse_iso20022_pacs008(xml_data):
    try:
        root = ET.fromstring(xml_data)
        transaction_id = root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}InstrId').text
        amount = round_to_two_decimals(float(root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}IntrBkSttlmAmt').text))
        currency = root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}IntrBkSttlmAmt').attrib['Ccy']

        debtor = {
            "name": root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Dbtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Nm').text,
            "phones": [phone.text for phone in root.findall('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Dbtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}PstlAdr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Phne')],
            "email": root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Dbtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}CtctDtls/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}EmailAdr').text,
            "address": root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Dbtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}PstlAdr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}StrtNm').text
        }

        creditor = {
            "name": root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Cdtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Nm').text,
            "phones": [phone.text for phone in root.findall('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Cdtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}PstlAdr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Phne')],
            "email": root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Cdtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}CtctDtls/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}EmailAdr').text,
            "address": root.find('.//{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}Cdtr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}PstlAdr/{urn:iso:std:iso:20022:tech:xsd:pacs.008.001.02}StrtNm').text
        }
        return {
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "debtor": debtor,
            "creditor": creditor
        }
    except Exception as e:
        return {"error": str(e)}

def dict_to_xml(tag, d):
    elem = ET.Element(tag)
    for key, val in d.items():
        child = ET.Element(key)
        if isinstance(val, dict):
            child.extend(dict_to_xml(key, val))
        else:
            child.text = str(val)
        elem.append(child)
    return elem

@app.route('/api/outbound_payment.xml', methods=['POST'])
def outbound_payment_xml():
    xml_data = request.data
    parsed_data = parse_iso20022_pacs008(xml_data)
    if "error" in parsed_data:
        return jsonify(parsed_data), 400

    data = load_positions()
    currency = parsed_data['currency']
    amount = parsed_data['amount']

    if currency in data['balances']:
        data['balances'][currency] = round_to_two_decimals(data['balances'][currency] - amount)
    else:
        return jsonify({"error": f"Currency {currency} not found"}), 400

    today = datetime.today().strftime('%Y-%m-%d')
    if currency not in data['transactions']:
        data['transactions'][currency] = {}

    if today not in data['transactions'][currency]:
        data['transactions'][currency][today] = {"inbound": {"count": 0, "total_amount": 0.0},
                                                 "outbound": {"count": 0, "total_amount": 0.0}}

    data['transactions'][currency][today]["outbound"]["count"] += 1
    data['transactions'][currency][today]["outbound"]["total_amount"] = round_to_two_decimals(
        data['transactions'][currency][today]["outbound"]["total_amount"] + amount
    )

    save_positions(data)

    response = {
        **parsed_data,
        "status": "Outbound Processed",
        "new_position": round_to_two_decimals(data['balances'][currency]),
        "cdata_content": f"<![CDATA[This is a CDATA section for currency {currency}]]>"
    }

    response_xml = dict_to_xml('result', response)
    xml_str = ET.tostring(response_xml, encoding='unicode', method='xml')
    xml_str = xml_str.replace('&lt;![CDATA[', '<![CDATA[').replace(']]&gt;', ']]>')

    return Response(xml_str, content_type='application/xml')

@app.route('/api/inbound_payment.xml', methods=['POST'])
def inbound_payment_xml():
    xml_data = request.data
    parsed_data = parse_iso20022_pacs008(xml_data)
    if "error" in parsed_data:
        return jsonify(parsed_data), 400

    data = load_positions()
    currency = parsed_data['currency']
    amount = parsed_data['amount']

    if currency in data['balances']:
        data['balances'][currency] = round_to_two_decimals(data['balances'][currency] + amount)
    else:
        data['balances'][currency] = round_to_two_decimals(amount)

    today = datetime.today().strftime('%Y-%m-%d')
    if currency not in data['transactions']:
        data['transactions'][currency] = {}

    if today not in data['transactions'][currency]:
        data['transactions'][currency][today] = {"inbound": {"count": 0, "total_amount": 0.0},
                                                 "outbound": {"count": 0, "total_amount": 0.0}}

    data['transactions'][currency][today]["inbound"]["count"] += 1
    data['transactions'][currency][today]["inbound"]["total_amount"] = round_to_two_decimals(
        data['transactions'][currency][today]["inbound"]["total_amount"] + amount
    )

    save_positions(data)

    response = {
        **parsed_data,
        "status": "Inbound Processed",
        "new_position": round_to_two_decimals(data['balances'][currency]),
        "cdata_content": f"<![CDATA[This is a CDATA section for currency {currency}]]>"
    }

    response_xml = dict_to_xml('result', response)
    xml_str = ET.tostring(response_xml, encoding='unicode', method='xml')
    xml_str = xml_str.replace('&lt;![CDATA[', '<![CDATA[').replace(']]&gt;', ']]>')

    return Response(xml_str, content_type='application/xml')

@app.route('/api/outbound_payment.json', methods=['POST'])
def outbound_payment_json():
    request_data = request.json

    try:
        transaction_id = request_data['transaction_id']
        amount = round_to_two_decimals(request_data['amount'])
        currency = request_data['currency']
        debtor = request_data['debtor']
        creditor = request_data['creditor']
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    data = load_positions()

    if currency in data['balances']:
        data['balances'][currency] = round_to_two_decimals(data['balances'][currency] - amount)
    else:
        return jsonify({"error": f"Currency {currency} not found"}), 400

    today = datetime.today().strftime('%Y-%m-%d')
    if currency not in data['transactions']:
        data['transactions'][currency] = {}

    if today not in data['transactions'][currency]:
        data['transactions'][currency][today] = {"inbound": {"count": 0, "total_amount": 0.0},
                                                 "outbound": {"count": 0, "total_amount": 0.0}}

    data['transactions'][currency][today]["outbound"]["count"] += 1
    data['transactions'][currency][today]["outbound"]["total_amount"] = round_to_two_decimals(
        data['transactions'][currency][today]["outbound"]["total_amount"] + amount
    )

    save_positions(data)

    response = {
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "debtor": debtor,
        "creditor": creditor,
        "status": "Outbound Processed",
        "new_position": round_to_two_decimals(data['balances'][currency])
    }
    return jsonify(response), 200

@app.route('/api/inbound_payment.json', methods=['POST'])
def inbound_payment_json():
    request_data = request.json

    try:
        transaction_id = request_data['transaction_id']
        amount = round_to_two_decimals(request_data['amount'])
        currency = request_data['currency']
        debtor = request_data['debtor']
        creditor = request_data['creditor']
    except KeyError as e:
        return jsonify({"error": f"Missing key: {str(e)}"}), 400

    data = load_positions()

    if currency in data['balances']:
        data['balances'][currency] = round_to_two_decimals(data['balances'][currency] + amount)
    else:
        data['balances'][currency] = round_to_two_decimals(amount)

    today = datetime.today().strftime('%Y-%m-%d')
    if currency not in data['transactions']:
        data['transactions'][currency] = {}

    if today not in data['transactions'][currency]:
        data['transactions'][currency][today] = {"inbound": {"count": 0, "total_amount": 0.0},
                                                 "outbound": {"count": 0, "total_amount": 0.0}}

    data['transactions'][currency][today]["inbound"]["count"] += 1
    data['transactions'][currency][today]["inbound"]["total_amount"] = round_to_two_decimals(
        data['transactions'][currency][today]["inbound"]["total_amount"] + amount
    )

    save_positions(data)

    response = {
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "debtor": debtor,
        "creditor": creditor,
        "status": "Inbound Processed",
        "new_position": round_to_two_decimals(data['balances'][currency])
    }
    return jsonify(response), 200

@app.route('/api/positions', methods=['POST'])
def get_positions():
    clear_old_positions()
    request_data = request.json
    data = load_positions()
    today = datetime.today().strftime('%Y-%m-%d')

    if not isinstance(request_data, list):
        return jsonify({"error": "Request body must be a list of currencies"}), 400

    results = []
    for currency in request_data:
        if currency in data['balances']:
            transactions = data['transactions'].get(currency, {}).get(today,
                                                                      {"inbound": {"count": 0, "total_amount": 0.0},
                                                                       "outbound": {"count": 0, "total_amount": 0.0}})
            results.append({
                "currency": currency,
                "balance": round_to_two_decimals(data['balances'][currency]),
                "value_date": today,
                "inbound": {
                    "count": transactions["inbound"]["count"],
                    "total_amount": round_to_two_decimals(transactions["inbound"]["total_amount"])
                },
                "outbound": {
                    "count": transactions["outbound"]["count"],
                    "total_amount": round_to_two_decimals(transactions["outbound"]["total_amount"])
                }
            })
        else:
            results.append({
                "currency": currency,
                "balance": 0.00,
                "value_date": today,
                "inbound": {"count": 0, "total_amount": 0.00},
                "outbound": {"count": 0, "total_amount": 0.00}
            })

    return jsonify(results), 200

@app.route('/api/positions2', methods=['GET'])
def get_all_positions():
    clear_old_positions()
    data = load_positions()
    today = datetime.today().strftime('%Y-%m-%d')

    results = []
    for currency in data['balances']:
        transactions = data['transactions'].get(currency, {}).get(today,
                                                                  {"inbound": {"count": 0, "total_amount": 0.0},
                                                                   "outbound": {"count": 0, "total_amount": 0.0}})
        results.append({
            "currency": currency,
            "balance": round_to_two_decimals(data['balances'][currency]),
            "value_date": today,
            "inbound": {
                "count": transactions["inbound"]["count"],
                "total_amount": round_to_two_decimals(transactions["inbound"]["total_amount"])
            },
            "outbound": {
                "count": transactions["outbound"]["count"],
                "total_amount": round_to_two_decimals(transactions["outbound"]["total_amount"])
            }
        })

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
