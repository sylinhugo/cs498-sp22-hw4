import json
from flask import Flask, request, jsonify, make_response
import subprocess
from pyhive import hive

app = Flask(__name__)


def fetch_data(params: str) -> list:
    query = "SELECT clicks FROM searchlog where term="
    query += "'" + params + "'"
    conn = hive.Connection(host="localhost", port=10000, username="hugo051697")
    cursor = conn.cursor()
    cursor.execute(query)

    res = cursor.fetchall()
    res_list = list(res)
    res_str = "".join(res_list[0])
    res_list = res_str[1:-1].split(",")  # list

    return res_list  # ['str: str', ...]


def aggregate_count(params: str, x: list) -> int:
    total = 0

    for i in range(len(x)):
        for j in range(len(x[i])):
            key, val = x[i][j].split(":")
            key = key[1:-1]
            print(key)
            if key == params:
                total += int(val)

    return total


@app.route("/")
def index():
    return jsonify(success=True)


@app.route("/results", methods=["POST"])
def get_results():
    print("---------- /results ----------")
    params = json.loads(request.data)
    print(params)
    params = params["term"]
    print(params)

    query = "SELECT clicks FROM searchlog where term="
    query += "'" + params + "'"

    conn = hive.Connection(host="localhost", port=10000, username="hugo051697")
    cursor = conn.cursor()
    cursor.execute(query)

    res = cursor.fetchall()
    res = list(res)
    res = res[0]
    res_str = "".join(res)

    res_str = res_str[1:-1].split(",")
    print(type(res_str))
    print(res_str)

    tmp_dict = dict()
    for i in range(len(res_str)):
        key, val = res_str[i].split(":")
        key = key[1:-1]
        tmp_dict[key] = int(val)

    clean_res = {"results": json.dumps(tmp_dict)}
    tmp = clean_res["results"]
    tmp = tmp.replace('"', "'")
    print(tmp)

    clean_res["results"] = tmp
    print(clean_res)

    return clean_res


@app.route("/trends", methods=["POST"])
def get_trends():
    print("---------- /trends ----------")
    params = json.loads(request.data)
    print(params)
    params = params["term"]
    print(params)

    query = "SELECT clicks FROM searchlog where term="
    query += "'" + params + "'"

    conn = hive.Connection(host="localhost", port=10000, username="hugo051697")
    cursor = conn.cursor()
    cursor.execute(query)
    res = cursor.fetchall()

    res_str = list(res)[0]

    res_str = "".join(res_str)

    res_str = res_str[1:-1].split(",")
    print(type(res_str))
    print(res_str)

    total = 0
    for i in range(len(res_str)):
        key, val = res_str[i].split(":")
        total += int(val)

    clean_res = {"clicks": total}
    print(clean_res)

    return jsonify(clean_res)


@app.route("/popularity", methods=["POST"])
def get_popularity():
    print("---------- /popularity ----------")
    params = json.loads(request.data)
    print(params)
    params = params["url"]
    print(params)

    terms = [
        "Portland",
        "Portland University",
        "Portland Computer",
        "Portland Vikings",
        "Portland Degrees",
    ]
    temp = []  # a list of list

    print(params)

    for item in terms:
        temp.append(fetch_data(item))

    print(temp)
    res = aggregate_count(params, temp)

    final_res = {"clicks": res}
    print(final_res)

    return jsonify(final_res)


@app.route("/getBestTerms", methods=["POST"])
def get_best_terms():
    print("---------- /getBestTerms ----------")
    params = json.loads(request.data)
    print(params)
    params = params["website"]
    print(params)

    terms = [
        "Portland",
        "Portland University",
        "Portland Computer",
        "Portland Vikings",
        "Portland Degrees",
    ]
    temp = []  # a list of list
    res = []

    for item in terms:
        temp.append(fetch_data(item))

    print(temp)

    for j in range(len(temp)):
        total = 0
        term_total = 0
        for k in range(len(temp[j])):
            key, val = temp[j][k].split(":")
            key = key[1:-1]
            total += int(val)
            print(key, params)
            if key == params:
                term_total += int(val)

        print(term_total, term_total / total)

        if term_total != 0 and term_total / total > 0.05:
            res.append(terms[j])

    final_res = {"best_terms": res}
    print(final_res)

    return jsonify(final_res)


# app.run(debug=True, host='0.0.0.0', port=80)
app.run(host="0.0.0.0", port=8080)
