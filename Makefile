ROOT_DIR   := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
OUTPUT_DIR := $(ROOT_DIR)/output
EGGS_DIR   := $(OUTPUT_DIR)/eggs
IMAGES_DIR := $(OUTPUT_DIR)/images
DOCS_DIR   := $(OUTPUT_DIR)/docs

CONTAINER_API_NAME        := shrimp-api
CONTAINER_BASE_NAME       := shrimp-base
CONTAINER_CLI_NAME        := shrimp-cli
CONTAINER_CONTROLLER_NAME := shrimp-controller
CONTAINER_CRON_NAME       := shrimp-cron
CONTAINER_DB_NAME         := shrimp-db
CONTAINER_DB_DATA_NAME    := shrimp-db-data
CONTAINER_FRONTEND_NAME   := shrimp-frontend
CONTAINER_PLUGINS_NAME    := shrimp-base-plugins

# -----------------------------------------------------------------------------

define build_egg
    cd $(1) && rm -rf dist && python setup.py bdist_wheel && cp dist/* $(2) && rm -rf dist build
endef

define dump_image
    docker save "$(1)" | bzip2 -c -9 > "$(2)/$(1).tar.bz2"
endef

# -----------------------------------------------------------------------------

build_eggs: build_backend_eggs build_shrimplib_eggs build_shrimpcli_eggs build_plugins_eggs
build_backend_eggs: build_api_eggs build_common_eggs build_controller_eggs build_ansible_eggs build_monitoring_eggs build_migration_eggs build_docker_eggs
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

build_migration_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/migration","$(EGGS_DIR)")

build_docker_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/backend/docker","$(EGGS_DIR)")

build_shrimplib_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/shrimplib","$(EGGS_DIR)")

build_shrimpcli_eggs: clean_eggs make_egg_directory
	$(call build_egg,"$(ROOT_DIR)/shrimpcli","$(EGGS_DIR)")

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

make_image_directory: make_output_directory
	mkdir -p "$(IMAGES_DIR)" || true

make_docs_directory: make_output_directory
	mkdir -p "$(DOCS_DIR)" || true

make_output_directory:
	mkdir -p "$(OUTPUT_DIR)" || true


# -----------------------------------------------------------------------------

build_ui: clean_ui npm_install
	cd "$(ROOT_DIR)/ui" && npm run build

npm_install:
	cd "$(ROOT_DIR)/ui" && npm install && npm run typings install

clean_ui:
	rm -rf "$(ROOT_DIR)/ui/build"

# -----------------------------------------------------------------------------


build_containers: build_container_api build_container_controller build_container_frontend build_container_db build_container_db_data build_container_cron
build_containers_dev: copy_example_keys build_containers

build_container_api: build_container_plugins
	docker build -f "$(ROOT_DIR)/containerization/backend-api.dockerfile" --tag $(CONTAINER_API_NAME) --rm "$(ROOT_DIR)"

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

build_container_db_data:
	docker build -f "$(ROOT_DIR)/containerization/db-data.dockerfile" --tag $(CONTAINER_DB_DATA_NAME) --pull --rm "$(ROOT_DIR)"

build_container_base: build_eggs
	docker build -f "$(ROOT_DIR)/containerization/backend-base.dockerfile" --tag $(CONTAINER_BASE_NAME) --pull --rm "$(ROOT_DIR)"

build_container_plugins: build_container_base
	docker build -f "$(ROOT_DIR)/containerization/backend-plugins.dockerfile" --tag $(CONTAINER_PLUGINS_NAME) --rm "$(ROOT_DIR)"

# -----------------------------------------------------------------------------


dump_images: dump_image_api dump_image_controller dump_image_frontend dump_image_db dump_image_db_data dump_image_cron

dump_image_api: make_image_directory
	$(call dump_image,$(CONTAINER_API_NAME),$(IMAGES_DIR))

dump_image_controller: make_image_directory
	$(call dump_image,$(CONTAINER_CONTROLLER_NAME),$(IMAGES_DIR))

dump_image_frontend: make_image_directory
	$(call dump_image,$(CONTAINER_FRONTEND_NAME),$(IMAGES_DIR))

dump_image_db: make_image_directory
	$(call dump_image,$(CONTAINER_DB_NAME),$(IMAGES_DIR))

dump_image_db_data: make_image_directory
	$(call dump_image,$(CONTAINER_DB_DATA_NAME),$(IMAGES_DIR))

dump_image_cron: make_image_directory
	$(call dump_image,$(CONTAINER_CRON_NAME),$(IMAGES_DIR))

# -----------------------------------------------------------------------------

html_docs: make_docs_directory
	cd "$(ROOT_DIR)/docs" && make html && mv build/html "$(DOCS_DIR)"

# -----------------------------------------------------------------------------


copy_example_keys:
	cp "$(ROOT_DIR)/containerization/files/ansible_ssh_keyfile.pem" "$(ROOT_DIR)" && \
	cp "$(ROOT_DIR)/containerization/files/nginx-selfsigned.key" "$(ROOT_DIR)/ssl.key" && \
	cp "$(ROOT_DIR)/containerization/files/nginx-selfsigned.crt" "$(ROOT_DIR)/ssl.crt" && \
	cp "$(ROOT_DIR)/containerization/files/nginx-dhparam.pem" "$(ROOT_DIR)/ssl-dhparam.pem" && \
	cp "$(ROOT_DIR)/containerization/files/config.yaml" "$(ROOT_DIR)" && \
	cp "$(ROOT_DIR)/containerization/files/mongodb.pem" "$(ROOT_DIR)" && \
	cp "$(ROOT_DIR)/containerization/files/mongodb-ca.crt" "$(ROOT_DIR)" && \
	chmod 0600 "$(ROOT_DIR)/ansible_ssh_keyfile.pem"
