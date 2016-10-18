ROOT_DIR   := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
OUTPUT_DIR := $(ROOT_DIR)/output
EGGS_DIR   := $(OUTPUT_DIR)/eggs

CONTAINER_API_NAME        := cephlcm-api
CONTAINER_API_ROOTED_NAME := cephlcm-api-rooted
CONTAINER_BASE_NAME       := cephlcm-base
CONTAINER_CLI_NAME        := cephlcm-cli
CONTAINER_CONTROLLER_NAME := cephlcm-controller
CONTAINER_CRON_NAME       := cephlcm-cron
CONTAINER_DB_NAME         := cephlcm-db
CONTAINER_FRONTEND_NAME   := cephlcm-frontend
CONTAINER_PLUGINS_NAME    := cephlcm-base-plugins

# -----------------------------------------------------------------------------

define build_egg
    cd $(1) && rm -rf dist && python setup.py bdist_wheel && cp dist/* $(2) && rm -rf dist build
endef

# -----------------------------------------------------------------------------

build_eggs: build_backend_eggs build_cephlcmlib_eggs build_cephlcmcli_eggs build_plugins_eggs
build_backend_eggs: build_api_eggs build_common_eggs build_controller_eggs build_ansible_eggs build_monitoring_eggs
build_plugins_eggs: build_alerts_eggs build_playbook_eggs
build_alerts_eggs: build_email_eggs
build_playbook_eggs: build_deploy_cluster_eggs build_helloworld_eggs build_server_discovery_eggs build_add_osd_eggs build_remove_osd_eggs build_purge_cluster_eggs

build_api_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/api","$(EGGS_DIR)")

build_common_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/common","$(EGGS_DIR)")

build_controller_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/controller","$(EGGS_DIR)")

build_ansible_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/ansible","$(EGGS_DIR)")

build_monitoring_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/monitoring","$(EGGS_DIR)")

build_cephlcmlib_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/cephlcmlib","$(EGGS_DIR)")

build_cephlcmcli_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/cephlcmcli","$(EGGS_DIR)")

build_email_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/plugins/alerts/emails","$(EGGS_DIR)")

build_deploy_cluster_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/deploy_cluster","$(EGGS_DIR)")

build_helloworld_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/playbook_helloworld","$(EGGS_DIR)")

build_server_discovery_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/server_discovery","$(EGGS_DIR)")

build_add_osd_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/add_osd","$(EGGS_DIR)")

build_remove_osd_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/remove_osd","$(EGGS_DIR)")

build_purge_cluster_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/plugins/playbook/purge_cluster","$(EGGS_DIR)")

clean_eggs:
	rm -rf "$(OUTPUT_DIR)"

make_egg_directory: make_output_directory
	mkdir -p "$(EGGS_DIR)" || true

make_output_directory:
	mkdir -p "$(OUTPUT_DIR)" || true

# -----------------------------------------------------------------------------

build_ui: clean_ui npm_install
	cd "$(ROOT_DIR)/ui" && npm run build

npm_install:
	cd "$(ROOT_DIR)/ui" && npm install

clean_ui:
	rm -rf "$(ROOT_DIR)/ui/build"

# -----------------------------------------------------------------------------


build_containers: build_container_api build_container_api_rooted build_container_controller build_container_frontend build_container_db build_container_cron
build_containers_dev: copy_example_keys build_containers

build_container_api: build_container_plugins
	docker build -f "$(ROOT_DIR)/containerization/backend-api.dockerfile" --tag $(CONTAINER_API_NAME) --rm "$(ROOT_DIR)"

build_container_api_rooted: build_container_api
	docker build -f "$(ROOT_DIR)/containerization/backend-api-rooted.dockerfile" --tag $(CONTAINER_API_ROOTED_NAME) --rm "$(ROOT_DIR)"

build_container_controller: build_container_plugins
	docker build -f "$(ROOT_DIR)/containerization/backend-controller.dockerfile" --tag $(CONTAINER_CONTROLLER_NAME) --rm "$(ROOT_DIR)"

build_container_cron: build_container_controller
	docker build -f "$(ROOT_DIR)/containerization/backend-cron.dockerfile" --tag $(CONTAINER_CRON_NAME) --rm "$(ROOT_DIR)"

build_container_frontend: build_ui
	docker build -f "$(ROOT_DIR)/containerization/frontend.dockerfile" --tag $(CONTAINER_FRONTEND_NAME) --pull --rm "$(ROOT_DIR)"

build_container_cli: build_eggs
	docker build -f "$(ROOT_DIR)/containerization/cli.dockerfile" --tag $(CONTAINER_CLI_NAME) --pull --rm "$(ROOT_DIR)"

build_container_db:
	docker build -f "$(ROOT_DIR)/containerization/db.dockerfile" --tag $(CONTAINER_DB_NAME) --pull --rm "$(ROOT_DIR)"

build_container_base: build_eggs
	docker build -f "$(ROOT_DIR)/containerization/backend-base.dockerfile" --tag $(CONTAINER_BASE_NAME) --pull --rm "$(ROOT_DIR)"

build_container_plugins: build_container_base
	docker build -f "$(ROOT_DIR)/containerization/backend-plugins.dockerfile" --tag $(CONTAINER_PLUGINS_NAME) --rm "$(ROOT_DIR)"

copy_example_keys:
	cp "$(ROOT_DIR)/containerization/files/ansible_ssh_keyfile.pem" "$(ROOT_DIR)" && \
	cp "$(ROOT_DIR)/containerization/files/nginx-selfsigned.key" "$(ROOT_DIR)/ssl.key" && \
	cp "$(ROOT_DIR)/containerization/files/nginx-selfsigned.crt" "$(ROOT_DIR)/ssl.crt" && \
	cp "$(ROOT_DIR)/containerization/files/nginx-dhparam.pem" "$(ROOT_DIR)/ssl-dhparam.pem"
