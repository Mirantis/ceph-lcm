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


db_container="cephlcm_database_1"


while getopts "c:h" opt; do
  case $opt in
    h)
      echo "Run Decapod migrations."
      echo ""
      echo "This command runs decapod-migration CLI script, connected "
      echo "to correct database"
      echo "Use --help command to get help from CLI script."
      echo ""
      echo "${0} [-c container_with_db_data] command" >&2
      exit 0
      ;;
    c)
      db_container="${OPTARG}"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done


shift $(($OPTIND - 1))
command="$@"


docker run \
    --rm \
    -it \
    --network "container:${db_container}" \
    decapod/migrations $command
