# coding: utf-8

import glob
import json
import jinja2
import datetime
import collections

from contextlib import suppress


def onboarding_generate():
    nodes = dict()
    epoches = set()

    for epoch_file in sorted(glob.glob("onboarding/epoches/*.txt")):
        epoch_no = int(epoch_file.split("/")[-1][0:3])
        epoches.add(epoch_no)

        with open(epoch_file) as f:
            for line in f:
                njson = json.loads(line)
                node_pubkey = njson["testnet_pk"]
                node_position = njson["onboarding_number"]

                bonus_13, bonus_207 = None, None
                credits_64, credits_64p = None, None

                with suppress(TypeError):
                    cs = njson["tn_calculated_stats"]
                    bonus_13 = "%.2f" % (cs["percent_bonus_last_13_epochs"] * 100)
                    bonus_207 = "%.2f" % (cs["percent_bonus_since_aug1_2021"] * 100)
                    credits_64 = int(cs["vote_credits_last_64_epochs"])
                    credits_64p = "%.2f" % (cs["vote_credit_score"] * 100)

                if node_pubkey not in nodes:
                    nodes[node_pubkey] = {
                        "testnet_pk": node_pubkey,
                        "mainnet_beta_pk": njson["mainnet_beta_pk"],
                        "tds_onboarding_group": njson["tds_onboarding_group"],
                        "positions": collections.defaultdict(dict),
                    }

                nodes[node_pubkey]["bonus_13"] = bonus_13
                nodes[node_pubkey]["bonus_207"] = bonus_207
                nodes[node_pubkey]["credits_64"] = credits_64
                nodes[node_pubkey]["credits_64p"] = credits_64p
                nodes[node_pubkey]["positions"][epoch_no] = node_position

    epoches = list(sorted(epoches))

    nodes_clean = dict()
    for node_pubkey, node in nodes.items():
        if any(node["positions"].values()):
            nodes_clean[node_pubkey] = node

    with open("onboarding/www/template.html") as f:
        template = jinja2.Template(f.read())

    with open("onboarding/www/index.html", "w+") as w:
        w.write(
            template.render(
                nodes=nodes_clean,
                epoches=epoches,
                datetime=datetime.datetime.utcnow()
            )
        )


if __name__ == "__main__":
    onboarding_generate()