# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Translation rule for cloud_sql_instances feature."""
from typing import Dict, List
from app2run.common.util import generate_output_flags, \
    get_feature_key_from_input
_ALLOW_CLOUD_SQL_INSTANCES_KEY = 'beta_settings.cloud_sql_instances'

def traqnslate_cloud_sql_instances_features(input_data: Dict, value_limited_features: Dict) \
    -> List[str]:
    """Translate cloud_sql_instances to the equivalent Cloud Run add-cloudsql-instances flag."""
    output_values: List[str] = []
    output_flags: List[str] = []
    cloud_sql_instances_key_from_input = get_feature_key_from_input(input_data, \
        [_ALLOW_CLOUD_SQL_INSTANCES_KEY])
    if cloud_sql_instances_key_from_input:
        feature = value_limited_features[cloud_sql_instances_key_from_input]
        cloud_sql_instances_value = input_data[cloud_sql_instances_key_from_input]
        instance_connections = cloud_sql_instances_value.split(',')

        for connection in instance_connections:
            if feature.validate(connection):
                output_values.append(connection)
    if len(output_values) > 0:
        output_flags += generate_output_flags(feature.flags, ','.join(output_values))
    return output_flags
