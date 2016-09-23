ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
OUTPUT_DIR := $(ROOT_DIR)/output
EGGS_DIR := $(OUTPUT_DIR)/eggs

# -----------------------------------------------------------------------------

define build_egg
    cd $(1) && rm -rf dist && python setup.py sdist && cp dist/* $(2)
endef

# -----------------------------------------------------------------------------

build_eggs: build_backend_eggs build_cephlcmlib_eggs build_cephlcmcli_eggs build_plugins_eggs
build_backend_eggs: build_api_eggs build_common_eggs build_controller_eggs
build_plugins_eggs: build_alerts_eggs build_playbook_eggs
build_alerts_eggs: build_email_eggs
build_playbook_eggs: build_deploy_cluster_eggs build_helloworld_eggs build_server_discovery_eggs

build_api_eggs: clean make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/api","$(EGGS_DIR)")

build_common_eggs: clean make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/common","$(EGGS_DIR)")

build_controller_eggs: clean make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/controller","$(EGGS_DIR)")

build_cephlcmlib_eggs:
	$(call build_egg,"$(ROOT_DIR)/cephlcmlib","$(EGGS_DIR)")

build_cephlcmcli_eggs:
	$(call build_egg,"$(ROOT_DIR)/cephlcmcli","$(EGGS_DIR)")

build_email_eggs:
	$(call build_egg,"$(ROOT_DIR)/plugins/alerts/emails","$(EGGS_DIR)")

build_deploy_cluster_eggs:
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/deploy_cluster","$(EGGS_DIR)")

build_helloworld_eggs:
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/playbook_helloworld","$(EGGS_DIR)")

build_server_discovery_eggs:
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/server_discovery","$(EGGS_DIR)")

clean:
	rm -rf "$(OUTPUT_DIR)"

make_egg_directory: make_output_directory
	mkdir -p "$(EGGS_DIR)" || true

make_output_directory:
	mkdir -p "$(OUTPUT_DIR)" || true
