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
      echo "Backup Decapod database on _stopped_ containers."
      echo ""
      echo "This scripts creates .tar.gz archive with contents of "
      echo "data volume filesystem."
      echo ""
      echo "${0} filename_to_backupto.tar.gz container_with_db_data" >&2
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done


backup_filename="${1:-backup.tar.gz}"
db_data_container="${2:-cephlcm_database_data_1}"
backup_dir="$(dirname "$(readlink -f ${backup_filename})")"

mkdir -p "${backup_dir}" || true
docker run \
    --rm \
    --volumes-from "${db_data_container}" \
    -v "${backup_dir}":/backup \
    ubuntu \
    bash -c "cd /backup && GZIP=-9 tar cvfz $(basename ${backup_filename}) /data"
