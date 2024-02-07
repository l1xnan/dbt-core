from dataclasses import dataclass, field
from dbt_common.dataclass_schema import dbtClassMixin
from dbt.artifacts.resources.v1.components import (
    ParsedNode,
    CompiledNode,
    NodeVersion,
    DeferRelation,
    MacroDependsOn,
)
from dbt_common.contracts.constraints import ModelLevelConstraint
from dbt.artifacts.resources.v1.config import ModelConfig, SeedConfig, TestConfig
from typing import Literal, Optional, List, Dict, Any
from dbt.artifacts.resources.types import NodeType, AccessType
from datetime import datetime


@dataclass
class AnalysisNode(CompiledNode):
    resource_type: Literal[NodeType.Analysis]


@dataclass
class HookNode(CompiledNode):
    resource_type: Literal[NodeType.Operation]
    index: Optional[int] = None


@dataclass
class ModelNode(CompiledNode):
    resource_type: Literal[NodeType.Model]
    access: AccessType = AccessType.Protected
    config: ModelConfig = field(default_factory=ModelConfig)
    constraints: List[ModelLevelConstraint] = field(default_factory=list)
    version: Optional[NodeVersion] = None
    latest_version: Optional[NodeVersion] = None
    deprecation_date: Optional[datetime] = None
    defer_relation: Optional[DeferRelation] = None


@dataclass
class SqlNode(CompiledNode):
    resource_type: Literal[NodeType.SqlOperation]


@dataclass
class SeedNode(ParsedNode):  # No SQLDefaults!
    resource_type: Literal[NodeType.Seed]
    config: SeedConfig = field(default_factory=SeedConfig)
    # seeds need the root_path because the contents are not loaded initially
    # and we need the root_path to load the seed later
    root_path: Optional[str] = None
    depends_on: MacroDependsOn = field(default_factory=MacroDependsOn)
    defer_relation: Optional[DeferRelation] = None


@dataclass
class SingularTestNode(CompiledNode):
    resource_type: Literal[NodeType.Test]
    # Was not able to make mypy happy and keep the code working. We need to
    # refactor the various configs.
    config: TestConfig = field(default_factory=TestConfig)  # type: ignore


@dataclass
class TestMetadata(dbtClassMixin):
    __test__ = False

    name: str = "test"  # dummy default to allow default in GenericTestNode. Should always be set.
    # kwargs are the args that are left in the test builder after
    # removing configs. They are set from the test builder when
    # the test node is created.
    kwargs: Dict[str, Any] = field(default_factory=dict)
    namespace: Optional[str] = None


@dataclass
class GenericTestNode(CompiledNode):
    resource_type: Literal[NodeType.Test]
    column_name: Optional[str] = None
    file_key_name: Optional[str] = None
    # Was not able to make mypy happy and keep the code working. We need to
    # refactor the various configs.
    config: TestConfig = field(default_factory=TestConfig)  # type: ignore
    attached_node: Optional[str] = None
    test_metadata: TestMetadata = field(default_factory=TestMetadata)
