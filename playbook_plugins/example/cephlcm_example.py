# -*- coding: utf-8 -*-
"""Example playbook plugin."""


from cephlcm.common import playbook_plugin


class Example(playbook_plugin.Base):

    DESCRIPTION = "This is an example playbook plugin for CephLCM"

    def make_playbook_configuration(self, servers, cluster_id=None):
        # TODO(Sergey Arkhipov): Implement when playbook configuration is done
        return {}

    def get_dynamic_inventory(self, playbook_configuration, cluster_id=None):
        return {
            "localhost": {
                "hosts": ["127.0.0.1"]
            },
            "_meta": {
                "hostvars": {
                    "localhost": {}
                }
            }
        }
