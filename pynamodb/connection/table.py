"""
PynamoDB Connection classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import asyncio
from pynamodb.async_util import wrap_secretly_sync_async_fn
from typing import Any, Dict, Mapping, Optional, Sequence

from pynamodb.connection.base import Connection, MetaTable, OperationSettings
from pynamodb.constants import DEFAULT_BILLING_MODE, KEY
from pynamodb.expressions.condition import Condition
from pynamodb.expressions.update import Action

class TableMeta(type):
    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)

        for attr_name, attr_value in attrs.items():
            suffix = "_async"
            if attr_name.endswith(suffix) and asyncio.iscoroutinefunction(attr_value):
                setattr(self, attr_name[:-len(suffix)], wrap_secretly_sync_async_fn(attr_value))


class TableConnection(metaclass=TableMeta):
    """
    A higher level abstraction over botocore
    """

    def __init__(
        self,
        table_name: str,
        region: Optional[str] = None,
        host: Optional[str] = None,
        connect_timeout_seconds: Optional[float] = None,
        read_timeout_seconds: Optional[float] = None,
        max_retry_attempts: Optional[int] = None,
        base_backoff_ms: Optional[int] = None,
        max_pool_connections: Optional[int] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ) -> None:
        self.table_name = table_name

        self.connection = Connection(region=region,
                                     host=host,
                                     connect_timeout_seconds=connect_timeout_seconds,
                                     read_timeout_seconds=read_timeout_seconds,
                                     max_retry_attempts=max_retry_attempts,
                                     base_backoff_ms=base_backoff_ms,
                                     max_pool_connections=max_pool_connections,
                                     extra_headers=extra_headers)

        if aws_access_key_id and aws_secret_access_key:
            self.connection.session.set_credentials(aws_access_key_id,
                                                    aws_secret_access_key,
                                                    aws_session_token)

    async def get_meta_table_async(self, refresh: bool = False) -> MetaTable:
        """
        Returns a MetaTable
        """
        return await self.connection.get_meta_table_async(self.table_name, refresh=refresh)

    async def get_operation_kwargs_async(
        self,
        hash_key: str,
        range_key: Optional[str] = None,
        key: str = KEY,
        attributes: Optional[Any] = None,
        attributes_to_get: Optional[Any] = None,
        actions: Optional[Sequence[Action]] = None,
        condition: Optional[Condition] = None,
        consistent_read: Optional[bool] = None,
        return_values: Optional[str] = None,
        return_consumed_capacity: Optional[str] = None,
        return_item_collection_metrics: Optional[str] = None,
        return_values_on_condition_failure: Optional[str] = None,
    ) -> Dict:
        return await self.connection.get_operation_kwargs(
            self.table_name,
            hash_key,
            range_key=range_key,
            key=key,
            attributes=attributes,
            attributes_to_get=attributes_to_get,
            actions=actions,
            condition=condition,
            consistent_read=consistent_read,
            return_values=return_values,
            return_consumed_capacity=return_consumed_capacity,
            return_item_collection_metrics=return_item_collection_metrics,
            return_values_on_condition_failure=return_values_on_condition_failure
        )

    async def delete_item_async(
        self,
        hash_key: str,
        range_key: Optional[str] = None,
        condition: Optional[Condition] = None,
        return_values: Optional[str] = None,
        return_consumed_capacity: Optional[str] = None,
        return_item_collection_metrics: Optional[str] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the DeleteItem operation and returns the result
        """
        return await self.connection.delete_item(
            self.table_name,
            hash_key,
            range_key=range_key,
            condition=condition,
            return_values=return_values,
            return_consumed_capacity=return_consumed_capacity,
            return_item_collection_metrics=return_item_collection_metrics,
            settings=settings,
        )

    async def update_item_async(
        self,
        hash_key: str,
        range_key: Optional[str] = None,
        actions: Optional[Sequence[Action]] = None,
        condition: Optional[Condition] = None,
        return_consumed_capacity: Optional[str] = None,
        return_item_collection_metrics: Optional[str] = None,
        return_values: Optional[str] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the UpdateItem operation
        """
        return await self.connection.update_item(
            self.table_name,
            hash_key,
            range_key=range_key,
            actions=actions,
            condition=condition,
            return_consumed_capacity=return_consumed_capacity,
            return_item_collection_metrics=return_item_collection_metrics,
            return_values=return_values,
            settings=settings,
        )

    async def put_item_async(
        self,
        hash_key: str,
        range_key: Optional[str] = None,
        attributes: Optional[Any] = None,
        condition: Optional[Condition] = None,
        return_values: Optional[str] = None,
        return_consumed_capacity: Optional[str] = None,
        return_item_collection_metrics: Optional[str] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the PutItem operation and returns the result
        """
        return await self.connection.put_item(
            self.table_name,
            hash_key,
            range_key=range_key,
            attributes=attributes,
            condition=condition,
            return_values=return_values,
            return_consumed_capacity=return_consumed_capacity,
            return_item_collection_metrics=return_item_collection_metrics,
            settings=settings,
        )

    async def batch_write_item_async(
        self,
        put_items: Optional[Any] = None,
        delete_items: Optional[Any] = None,
        return_consumed_capacity: Optional[str] = None,
        return_item_collection_metrics: Optional[str] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the batch_write_item operation
        """
        return await self.connection.batch_write_item(
            self.table_name,
            put_items=put_items,
            delete_items=delete_items,
            return_consumed_capacity=return_consumed_capacity,
            return_item_collection_metrics=return_item_collection_metrics,
            settings=settings,
        )

    async def batch_get_item_async(
        self,
        keys: Sequence[str],
        consistent_read: Optional[bool] = None,
        return_consumed_capacity: Optional[str] = None,
        attributes_to_get: Optional[Any] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the batch get item operation
        """
        return await self.connection.batch_get_item(
            self.table_name,
            keys,
            consistent_read=consistent_read,
            return_consumed_capacity=return_consumed_capacity,
            attributes_to_get=attributes_to_get,
            settings=settings,
        )

    async def get_item_async(
        self,
        hash_key: str,
        range_key: Optional[str] = None,
        consistent_read: bool = False,
        attributes_to_get: Optional[Any] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the GetItem operation and returns the result
        """
        return await self.connection.get_item(
            self.table_name,
            hash_key,
            range_key=range_key,
            consistent_read=consistent_read,
            attributes_to_get=attributes_to_get,
            settings=settings,
        )

    async def scan_async(
        self,
        filter_condition: Optional[Any] = None,
        attributes_to_get: Optional[Any] = None,
        limit: Optional[int] = None,
        return_consumed_capacity: Optional[str] = None,
        segment: Optional[int] = None,
        total_segments: Optional[int] = None,
        exclusive_start_key: Optional[str] = None,
        consistent_read: Optional[bool] = None,
        index_name: Optional[str] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the scan operation
        """
        return await self.connection.scan(
            self.table_name,
            filter_condition=filter_condition,
            attributes_to_get=attributes_to_get,
            limit=limit,
            return_consumed_capacity=return_consumed_capacity,
            segment=segment,
            total_segments=total_segments,
            exclusive_start_key=exclusive_start_key,
            consistent_read=consistent_read,
            index_name=index_name,
            settings=settings,
        )

    async def query_async(
        self,
        hash_key: str,
        range_key_condition: Optional[Condition] = None,
        filter_condition: Optional[Any] = None,
        attributes_to_get: Optional[Any] = None,
        consistent_read: bool = False,
        exclusive_start_key: Optional[Any] = None,
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        return_consumed_capacity: Optional[str] = None,
        scan_index_forward: Optional[bool] = None,
        select: Optional[str] = None,
        settings: OperationSettings = OperationSettings.default,
    ) -> Dict:
        """
        Performs the Query operation and returns the result
        """
        return await self.connection.query(
            self.table_name,
            hash_key,
            range_key_condition=range_key_condition,
            filter_condition=filter_condition,
            attributes_to_get=attributes_to_get,
            consistent_read=consistent_read,
            exclusive_start_key=exclusive_start_key,
            index_name=index_name,
            limit=limit,
            return_consumed_capacity=return_consumed_capacity,
            scan_index_forward=scan_index_forward,
            select=select,
            settings=settings,
        )

    async def describe_table_async(self) -> Dict:
        """
        Performs the DescribeTable operation and returns the result
        """
        return await self.connection.describe_table_async(self.table_name)

    async def delete_table_async(self) -> Dict:
        """
        Performs the DeleteTable operation and returns the result
        """
        return await self.connection.delete_table_async(self.table_name)

    async def update_time_to_live_async(self, ttl_attr_name: str) -> Dict:
        """
        Performs the UpdateTimeToLive operation and returns the result
        """
        return await self.connection.update_time_to_live_async(self.table_name, ttl_attr_name)

    async def update_table_async(
        self,
        read_capacity_units: Optional[int] = None,
        write_capacity_units: Optional[int] = None,
        global_secondary_index_updates: Optional[Any] = None,
    ) -> Dict:
        """
        Performs the UpdateTable operation and returns the result
        """
        return await self.connection.update_table_async(
            self.table_name,
            read_capacity_units=read_capacity_units,
            write_capacity_units=write_capacity_units,
            global_secondary_index_updates=global_secondary_index_updates)

    async def create_table_async(
        self,
        attribute_definitions: Optional[Any] = None,
        key_schema: Optional[Any] = None,
        read_capacity_units: Optional[int] = None,
        write_capacity_units: Optional[int] = None,
        global_secondary_indexes: Optional[Any] = None,
        local_secondary_indexes: Optional[Any] = None,
        stream_specification: Optional[Dict] = None,
        billing_mode: str = DEFAULT_BILLING_MODE,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        Performs the CreateTable operation and returns the result
        """
        return await self.connection.create_table_async(
            self.table_name,
            attribute_definitions=attribute_definitions,
            key_schema=key_schema,
            read_capacity_units=read_capacity_units,
            write_capacity_units=write_capacity_units,
            global_secondary_indexes=global_secondary_indexes,
            local_secondary_indexes=local_secondary_indexes,
            stream_specification=stream_specification,
            billing_mode=billing_mode,
            tags=tags
        )
