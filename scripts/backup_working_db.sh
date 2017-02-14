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

echo "THIS SCRIPT IS DEPRECATED. Use backup_working_db_native.sh instead." 1>&2

while getopts ":h" opt; do
  case $opt in
    h)
      echo "Backup Decapod database on _working_ containers."
      echo ""
      echo "This scripts creates .tar.gz archive with contents of "
      echo "mongodump."
      echo ""
      echo "${0} filename_to_backupto.tar.gz container_with_db" >&2
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done


backup_filename="${1:-backup.tar.gz}"
db_container="${2:-cephlcm_database_1}"
backup_dir="$(dirname "$(readlink -f "${backup_filename}")")"

mkdir -p "${backup_dir}" || true
docker exec "${db_container}" bash -c "(mkdir -p /backup || true) && cd /backup && mongodump --gzip --ssl && cd / && GZIP=-9 tar cvfz /backup.tar.gz /backup && rm -rf /backup" \
    && docker cp "${db_container}":/backup.tar.gz "${backup_dir}/$(basename "${backup_filename}")" \
    && docker exec "${db_container}" rm /backup.tar.gz
