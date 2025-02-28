"""
Copyright 2019 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""

from typing import List, Dict

from gs_quant.analytics.common import TYPE, DATA_ROW, PROCESSOR, REFERENCE, PARAMETER, ENTITY_ID, ENTITY_TYPE
from gs_quant.entities.entity import Entity
from gs_quant.errors import MqValueError


def is_of_builtin_type(obj):
    return type(obj).__module__ in ('builtins', '__builtin__')


def resolve_entities(reference_list: List[Dict]):
    """
    Utility function to fetch entities (assets, countries, etc.). Allows us to split functionality that requires data
    fetching.
    :param reference_list: A list of entity references (entityId and entityType dictionaries)
    :return: None
    """
    entity_cache = {}
    for reference in reference_list:
        # Create a hash key of the entity data so we don't fetch the same entity multiple times.
        key = hash((reference.get(ENTITY_ID), reference.get(ENTITY_TYPE)))
        if key in entity_cache:
            entity = entity_cache[key]
        else:
            entity = Entity.get(reference.get(ENTITY_ID), 'MQID', reference.get(ENTITY_TYPE))

        if reference[TYPE] == DATA_ROW:
            # If the reference is for a data row, simply set the entity of the row.
            reference[REFERENCE].entity = entity
        elif reference[TYPE] == PROCESSOR:
            # If the reference is for a processor, set the given parameter as the entity.
            setattr(reference[REFERENCE], reference[PARAMETER], entity)
            data_query_info = reference[REFERENCE].children.get(reference[PARAMETER])
            if not data_query_info:
                raise MqValueError(
                    f'{reference[PARAMETER]} does not exist in children of '
                    f'{reference[REFERENCE].__class__.__name__}')
            data_query_info.entity = entity


def get_rdate_cache_key(rule: str, currencies: List[str], exchanges: List[str]) -> str:
    return f'{rule}{currencies}{exchanges}'
