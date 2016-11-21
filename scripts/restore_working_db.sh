#!/bin/bash
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
      echo "Restore Shrimp database on _working_ containers."
      echo ""
      echo "This scripts restore .tar.gz archive with contents of "
      echo "mongodump."
      echo ""
      echo "${0} filename_with_backup.tar.gz container_with_db" >&2
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

docker cp "${backup_filename}" "${db_container}":/backup.tar.gz \
    && docker exec "${db_container}" bash -c 'cd / && tar xvf backup.tar.gz && cd backup && mongorestore --gzip --drop --ssl && cd / && rm -rf backup.tar.gz backup'
