# coding: utf-8

import glob
import json
import jinja2
import collections


def onboarding_generate():
    nodes = dict()
    epoches = set()

    for epoch_file in glob.glob("onboarding/epoches/*.txt"):
        epoch_no = int(epoch_file.split("/")[-1][0:3])
        epoches.add(epoch_no)

        with open(epoch_file) as f:
            for line in f:
                njson = json.loads(line)
                node_pubkey = njson["testnet_pk"]
                node_position = njson["onboarding_number"]

                if node_pubkey not in nodes:
                    nodes[node_pubkey] = {
                        "testnet_pk": node_pubkey,
                        "mainnet_beta_pk": njson["mainnet_beta_pk"],
                        "tds_onboarding_group": njson["tds_onboarding_group"],
                        "positions": collections.defaultdict(dict)
                    }
                nodes[node_pubkey]["positions"][epoch_no] = node_position

    epoches = list(sorted(epoches))

    nodes_clean = dict()
    for node_pubkey, node in nodes.items():
        if any(node["positions"].values()):
            nodes_clean[node_pubkey] = node

    with open("onboarding/www/template.html") as f:
        template = jinja2.Template(f.read())

    with open("onboarding/www/index.html", "w+") as w:
        w.write(template.render(nodes=nodes_clean, epoches=epoches))


if __name__ == "__main__":
    onboarding_generate()