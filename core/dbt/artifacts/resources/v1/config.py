from dbt_common.dataclass_schema import dbtClassMixin, ValidationError
from typing import Optional, List, Any, Dict, Union
from dataclasses import dataclass, field
from dbt_common.contracts.config.base import (
    BaseConfig,
    CompareBehavior,
    MergeBehavior,
)
from dbt_common.contracts.config.metadata import Metadata, ShowBehavior
from dbt_common.contracts.config.materialization import OnConfigurationChangeOption
from dbt.artifacts.resources.base import Docs
from dbt.artifacts.resources.types import ModelHookType, AccessType
from dbt.contracts.graph.utils import validate_color
from dbt import hooks


def list_str() -> List[str]:
    return []


def metas(*metas: Metadata) -> Dict[str, Any]:
    existing: Dict[str, Any] = {}
    for m in metas:
        existing = m.meta(existing)
    return existing


@dataclass
class ContractConfig(dbtClassMixin):
    enforced: bool = False
    alias_types: bool = True


@dataclass
class Hook(dbtClassMixin):
    sql: str
    transaction: bool = True
    index: Optional[int] = None


@dataclass
class NodeAndTestConfig(BaseConfig):
    enabled: bool = True
    # these fields are included in serialized output, but are not part of
    # config comparison (they are part of database_representation)
    alias: Optional[str] = field(
        default=None,
        metadata=CompareBehavior.Exclude.meta(),
    )
    schema: Optional[str] = field(
        default=None,
        metadata=CompareBehavior.Exclude.meta(),
    )
    database: Optional[str] = field(
        default=None,
        metadata=CompareBehavior.Exclude.meta(),
    )
    tags: Union[List[str], str] = field(
        default_factory=list_str,
        metadata=metas(ShowBehavior.Hide, MergeBehavior.Append, CompareBehavior.Exclude),
    )
    meta: Dict[str, Any] = field(
        default_factory=dict,
        metadata=MergeBehavior.Update.meta(),
    )
    group: Optional[str] = field(
        default=None,
        metadata=CompareBehavior.Exclude.meta(),
    )


@dataclass
class NodeConfig(NodeAndTestConfig):
    # Note: if any new fields are added with MergeBehavior, also update the
    # 'mergebehavior' dictionary
    materialized: str = "view"
    incremental_strategy: Optional[str] = None
    persist_docs: Dict[str, Any] = field(default_factory=dict)
    post_hook: List[Hook] = field(
        default_factory=list,
        metadata={"merge": MergeBehavior.Append, "alias": "post-hook"},
    )
    pre_hook: List[Hook] = field(
        default_factory=list,
        metadata={"merge": MergeBehavior.Append, "alias": "pre-hook"},
    )
    quoting: Dict[str, Any] = field(
        default_factory=dict,
        metadata=MergeBehavior.Update.meta(),
    )
    # This is actually only used by seeds. Should it be available to others?
    # That would be a breaking change!
    column_types: Dict[str, Any] = field(
        default_factory=dict,
        metadata=MergeBehavior.Update.meta(),
    )
    full_refresh: Optional[bool] = None
    # 'unique_key' doesn't use 'Optional' because typing.get_type_hints was
    # sometimes getting the Union order wrong, causing serialization failures.
    unique_key: Union[str, List[str], None] = None
    on_schema_change: Optional[str] = "ignore"
    on_configuration_change: OnConfigurationChangeOption = field(
        default_factory=OnConfigurationChangeOption.default
    )
    grants: Dict[str, Any] = field(
        default_factory=dict, metadata=MergeBehavior.DictKeyAppend.meta()
    )
    packages: List[str] = field(
        default_factory=list,
        metadata=MergeBehavior.Append.meta(),
    )
    docs: Docs = field(
        default_factory=Docs,
        metadata=MergeBehavior.Update.meta(),
    )
    contract: ContractConfig = field(
        default_factory=ContractConfig,
        metadata=MergeBehavior.Update.meta(),
    )

    def __post_init__(self):
        # we validate that node_color has a suitable value to prevent dbt-docs from crashing
        if self.docs.node_color:
            node_color = self.docs.node_color
            if not validate_color(node_color):
                raise ValidationError(
                    f"Invalid color name for docs.node_color: {node_color}. "
                    "It is neither a valid HTML color name nor a valid HEX code."
                )

        if (
            self.contract.enforced
            and self.materialized == "incremental"
            and self.on_schema_change not in ("append_new_columns", "fail")
        ):
            raise ValidationError(
                f"Invalid value for on_schema_change: {self.on_schema_change}. Models "
                "materialized as incremental with contracts enabled must set "
                "on_schema_change to 'append_new_columns' or 'fail'"
            )

    @classmethod
    def __pre_deserialize__(cls, data):
        data = super().__pre_deserialize__(data)
        for key in ModelHookType:
            if key in data:
                data[key] = [hooks.get_hook_dict(h) for h in data[key]]
        return data


@dataclass
class ModelConfig(NodeConfig):
    access: AccessType = field(
        default=AccessType.Protected,
        metadata=MergeBehavior.Update.meta(),
    )


@dataclass
class SeedConfig(NodeConfig):
    materialized: str = "seed"
    delimiter: str = ","
    quote_columns: Optional[bool] = None

    @classmethod
    def validate(cls, data):
        super().validate(data)
        if data.get("materialized") and data.get("materialized") != "seed":
            raise ValidationError("A seed must have a materialized value of 'seed'")
