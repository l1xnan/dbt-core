from dataclasses import dataclass, field
from dbt.artifacts.resources.v1.macro import MacroDependsOn
from dbt.artifacts.resources.base import GraphResource, FileHash
from dbt.artifacts.resources.v1.config import NodeConfig
from dbt_common.dataclass_schema import dbtClassMixin
from typing import Dict, List, Optional, Union


NodeVersion = Union[str, float]


@dataclass
class DependsOn(MacroDependsOn):
    nodes: List[str] = field(default_factory=list)

    def add_node(self, value: str):
        if value not in self.nodes:
            self.nodes.append(value)


@dataclass
class RefArgs(dbtClassMixin):
    name: str
    package: Optional[str] = None
    version: Optional[NodeVersion] = None

    @property
    def positional_args(self) -> List[str]:
        if self.package:
            return [self.package, self.name]
        else:
            return [self.name]

    @property
    def keyword_args(self) -> Dict[str, Optional[NodeVersion]]:
        if self.version:
            return {"version": self.version}
        else:
            return {}


@dataclass
class Docs(dbtClassMixin):
    show: bool = True
    node_color: Optional[str] = None


@dataclass
class HasRelationMetadata(dbtClassMixin):
    database: Optional[str]
    schema: str

    # Can't set database to None like it ought to be
    # because it messes up the subclasses and default parameters
    # so hack it here
    @classmethod
    def __pre_deserialize__(cls, data):
        data = super().__pre_deserialize__(data)
        if "database" not in data:
            data["database"] = None
        return data

    @property
    def quoting_dict(self) -> Dict[str, bool]:
        if hasattr(self, "quoting"):
            return self.quoting.to_dict(omit_none=True)
        else:
            return {}


@dataclass
class ParsedNodeMandatory(GraphResource, HasRelationMetadata):
    alias: str
    checksum: FileHash
    config: NodeConfig = field(default_factory=NodeConfig)

    @property
    def identifier(self):
        return self.alias
