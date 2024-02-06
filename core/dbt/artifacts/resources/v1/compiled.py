from dataclasses import dataclass, field
from dbt.artifacts.resources.v1.components import (
    ParsedNode,
    CompiledNode,
    NodeVersion,
    DeferRelation,
    MacroDependsOn,
)
from dbt_common.contracts.constraints import ModelLevelConstraint
from dbt.artifacts.resources.v1.config import ModelConfig, SeedConfig
from typing import Literal, Optional, List
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
