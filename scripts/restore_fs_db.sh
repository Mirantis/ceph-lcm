#!/bin/bash
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
set -eu -o pipefail


while getopts ":h" opt; do
  case $opt in
    h)
      echo "Restore Decapod database on _stopped_ containers."
      echo ""
      echo "This scripts restores .tar.gz archive with contents of "
      echo "data volume filesystem."
      echo ""
      echo "${0} filename_of_backup.tar.gz container_with_db_data" >&2
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done


backup_filename="$(readlink -f "${1:-backup.tar.gz}")"
db_data_container="${2:-cephlcm_database_data_1}"

docker run \
    --rm \
    --volumes-from "${db_data_container}" \
    -v "${backup_filename}":/backup.tar.gz \
    ubuntu bash -c "(mkdir -p /data || true) && cd /data && tar xvf /backup.tar.gz --strip 1"
