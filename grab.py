# coding: utf-8
""" Grab data from https://solana.foundation/validators-search
"""

import os
import json
import requests

SFDP_URL = "&".join((
    "https://kyc-api.vercel.app/api/validators/list?limit=100",
    "order_by=onboarding_number",
    "order=asc",
    "search_term=",
    "offset=%d"
))

RPC_ENDPOINT = "https://api.testnet.solana.com"


def fatal_error(message):
    print("Fatal error: %s" % message)
    exit(1)


def get_epoch():
    """ Get current epoch number from testnet RPC
    """
    r = requests.post(
        RPC_ENDPOINT,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getEpochInfo"}),
        headers={"Content-Type": "application/json"}
    )

    try:
        resp = r.json()
        return int(resp["result"]["epoch"])
    except Exception as e:
        fatal_error("Unable to parse response: status=%s, text=%s" % (
            r.status_code, r.text))

    fatal_error("Unable to get epoch no")


def grab_data():
    http = requests.Session()
    nodes = []

    for x in range(0, 50):
        url = SFDP_URL % (x * 99)
        print("Request %s" % url)
        d = http.get(url).json()

        if not d["data"]:
            break

        for row in d["data"]:
            nodes.append(json.dumps(row))

    nodes = list(set(nodes))
    return nodes


def flatten_json(y):
    """ JSON flattener from https://stackoverflow.com/a/51379007
    """
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out


def update_onboarding():
    """ Update onboarding numbers and save
    """
    os.makedirs("onboarding/epoches", exist_ok=True)

    epoch_no = get_epoch()
    print("Current epoch no: %d" % epoch_no)

    nodes = grab_data()
    print("Total nodes in set: %d" % len(nodes))

    with open("onboarding/epoches/%d.txt" % epoch_no, "w+") as w:
        for row in nodes:
            w.write(row + "\n")

    # Get csv keys
    csv_keys = [
        "testnet_pk",
        "mainnet_beta_pk",
        # "mn_calculated_stats",
        # "mn_calculated_stats_avg_self_stake",
        # "mn_calculated_stats_avg_skip_rate",
        # "mn_calculated_stats_bonus_and_baseline_percent",
        # "mn_calculated_stats_bonus_epochs_percent",
        # "mn_calculated_stats_num_bonus_last_10",
        # "mn_calculated_stats_percent_bonus_last_13_epochs",
        # "mn_calculated_stats_percent_bonus_since_aug1_2021",
        # "mn_calculated_stats_vote_credit_score",
        # "mn_calculated_stats_vote_credits_last_64_epochs",
        # "mn_keybase_username",
        # "mn_name",
        "onboarding_number",
        "state",
        "tds_onboarding_group",
        # "tn_calculated_stats",
        "tn_calculated_stats_avg_self_stake",
        "tn_calculated_stats_avg_skip_rate",
        "tn_calculated_stats_bonus_and_baseline_percent",
        "tn_calculated_stats_bonus_epochs_percent",
        "tn_calculated_stats_num_bonus_last_10",
        "tn_calculated_stats_percent_bonus_last_13_epochs",
        "tn_calculated_stats_percent_bonus_since_aug1_2021",
        "tn_calculated_stats_vote_credit_score",
        "tn_calculated_stats_vote_credits_last_64_epochs",
        "tn_name",
    ]

    # for row in nodes:
    #     row = flatten_json(json.loads(row))
    #     for key in row:
    #         csv_keys.add(key)
    #
    # print(sorted(csv_keys))
    # exit(-1)

    with open("onboarding/epoches/%d.csv" % epoch_no, "w+") as w:
        w.write(";".join(csv_keys) + "\n")

        for row in nodes:
            row = flatten_json(json.loads(row))
            data = []

            for key in csv_keys:
                try:
                    data.append("%s" % row[key])
                except KeyError:
                    data.append("")

            w.write(";".join(data) + "\n")


if __name__ == "__main__":
    update_onboarding()
