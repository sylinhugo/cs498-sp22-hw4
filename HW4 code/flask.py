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


@app.route("/results", methods=["GET"])
def get_results():
    params = request.args.get("term")
    query = "SELECT clicks FROM searchlog where term="
    query += "'" + params + "'"

    conn = hive.Connection(host="localhost", port=10000, username="hugo051697")
    cursor = conn.cursor()
    # cursor.execute("SELECT clicks FROM searchlog where term=\'‘Portland Degrees’\'")
    cursor.execute(query)

    # for result in cursor.fetchall():
    #     print(result)
    #     print(type(result))
    #     print(list(result))
    #     tmp = list(result)
    #     print(tmp[0])

    res = cursor.fetchall()
    res = list(res)
    res = res[0]
    res_str = "".join(res)
    print(type(res_str))
    print(res_str)

    res_str = res_str[1:-1].split(",")
    print(type(res_str))
    print(res_str)

    tmp_dict = dict()
    for i in range(len(res_str)):
        key, val = res_str[i].split(":")
        key = key[1:-1]
        tmp_dict[key] = int(val)

    print(tmp_dict.items())
    print("#####")
    clean_res = {"results": json.dumps(tmp_dict)}
    print(clean_res)

    return clean_res
    # return jsonify(clean_res)


@app.route("/trends", methods=["GET"])
def get_trends():
    params = request.args.get("term")
    query = "SELECT clicks FROM searchlog where term="
    query += "'" + params + "'"

    conn = hive.Connection(host="localhost", port=10000, username="hugo051697")
    cursor = conn.cursor()
    # cursor.execute("SELECT clicks FROM searchlog where term=\'‘Portland Degrees’\'")
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

    return jsonify(clean_res)


@app.route("/popularity", methods=["GET"])
def get_popularity():
    params = request.args.get("url")
    terms = [
        "‘Portland’",
        "‘Portland University’",
        "‘Portland Computer’",
        "‘Portland Vikings’",
        "‘Portland Degrees’",
    ]
    temp = []  # a list of list

    print(params)

    for item in terms:
        temp.append(fetch_data(item))

    print(temp)
    res = aggregate_count(params, temp)

    final_res = {"clicks": res}
    return jsonify(final_res)


@app.route("/getBestTerms", methods=["GET"])
def get_best_terms():
    params = request.args.get("website")

    terms = [
        "‘Portland’",
        "‘Portland University’",
        "‘Portland Computer’",
        "‘Portland Vikings’",
        "‘Portland Degrees’",
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

    return jsonify(final_res)


# app.run(debug=True, host='0.0.0.0', port=80)
app.run(host="0.0.0.0", port=8080)
