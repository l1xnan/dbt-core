from dataclasses import field, dataclass
from typing import Any, List, Optional, Dict, Union, Type

from dbt.artifacts.resources import (
    ExposureConfig,
    MetricConfig,
    SavedQueryConfig,
    SemanticModelConfig,
    NodeConfig,
    SeedConfig,
    TestConfig,
)
from dbt_common.contracts.config.base import BaseConfig, MergeBehavior, CompareBehavior
from dbt_common.contracts.config.metadata import Metadata, ShowBehavior
from dbt_common.dataclass_schema import (
    dbtClassMixin,
    ValidationError,
)
from dbt.contracts.util import Replaceable, list_str
from dbt.node_types import NodeType


def metas(*metas: Metadata) -> Dict[str, Any]:
    existing: Dict[str, Any] = {}
    for m in metas:
        existing = m.meta(existing)
    return existing


def insensitive_patterns(*patterns: str):
    lowercased = []
    for pattern in patterns:
        lowercased.append("".join("[{}{}]".format(s.upper(), s.lower()) for s in pattern))
    return "^({})$".format("|".join(lowercased))


@dataclass
class Hook(dbtClassMixin, Replaceable):
    sql: str
    transaction: bool = True
    index: Optional[int] = None


@dataclass
class SourceConfig(BaseConfig):
    enabled: bool = True


@dataclass
class UnitTestNodeConfig(NodeConfig):
    expected_rows: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EmptySnapshotConfig(NodeConfig):
    materialized: str = "snapshot"
    unique_key: Optional[str] = None  # override NodeConfig unique_key definition


@dataclass
class SnapshotConfig(EmptySnapshotConfig):
    strategy: Optional[str] = None
    unique_key: Optional[str] = None
    target_schema: Optional[str] = None
    target_database: Optional[str] = None
    updated_at: Optional[str] = None
    # Not using Optional because of serialization issues with a Union of str and List[str]
    check_cols: Union[str, List[str], None] = None

    @classmethod
    def validate(cls, data):
        super().validate(data)
        # Note: currently you can't just set these keys in schema.yml because this validation
        # will fail when parsing the snapshot node.
        if not data.get("strategy") or not data.get("unique_key") or not data.get("target_schema"):
            raise ValidationError(
                "Snapshots must be configured with a 'strategy', 'unique_key', "
                "and 'target_schema'."
            )
        if data.get("strategy") == "check":
            if not data.get("check_cols"):
                raise ValidationError(
                    "A snapshot configured with the check strategy must "
                    "specify a check_cols configuration."
                )
            if isinstance(data["check_cols"], str) and data["check_cols"] != "all":
                raise ValidationError(
                    f"Invalid value for 'check_cols': {data['check_cols']}. "
                    "Expected 'all' or a list of strings."
                )
        elif data.get("strategy") == "timestamp":
            if not data.get("updated_at"):
                raise ValidationError(
                    "A snapshot configured with the timestamp strategy "
                    "must specify an updated_at configuration."
                )
            if data.get("check_cols"):
                raise ValidationError("A 'timestamp' snapshot should not have 'check_cols'")
        # If the strategy is not 'check' or 'timestamp' it's a custom strategy,
        # formerly supported with GenericSnapshotConfig

        if data.get("materialized") and data.get("materialized") != "snapshot":
            raise ValidationError("A snapshot must have a materialized value of 'snapshot'")

    # Called by "calculate_node_config_dict" in ContextConfigGenerator
    def finalize_and_validate(self):
        data = self.to_dict(omit_none=True)
        self.validate(data)
        return self.from_dict(data)


@dataclass
class UnitTestConfig(BaseConfig):
    tags: Union[str, List[str]] = field(
        default_factory=list_str,
        metadata=metas(ShowBehavior.Hide, MergeBehavior.Append, CompareBehavior.Exclude),
    )
    meta: Dict[str, Any] = field(
        default_factory=dict,
        metadata=MergeBehavior.Update.meta(),
    )


RESOURCE_TYPES: Dict[NodeType, Type[BaseConfig]] = {
    NodeType.Metric: MetricConfig,
    NodeType.SemanticModel: SemanticModelConfig,
    NodeType.SavedQuery: SavedQueryConfig,
    NodeType.Exposure: ExposureConfig,
    NodeType.Source: SourceConfig,
    NodeType.Seed: SeedConfig,
    NodeType.Test: TestConfig,
    NodeType.Model: NodeConfig,
    NodeType.Snapshot: SnapshotConfig,
    NodeType.Unit: UnitTestConfig,
}


# base resource types are like resource types, except nothing has mandatory
# configs.
BASE_RESOURCE_TYPES: Dict[NodeType, Type[BaseConfig]] = RESOURCE_TYPES.copy()
BASE_RESOURCE_TYPES.update({NodeType.Snapshot: EmptySnapshotConfig})


def get_config_for(resource_type: NodeType, base=False) -> Type[BaseConfig]:
    if base:
        lookup = BASE_RESOURCE_TYPES
    else:
        lookup = RESOURCE_TYPES
    return lookup.get(resource_type, NodeConfig)
