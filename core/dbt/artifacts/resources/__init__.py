from dbt.artifacts.resources.base import BaseResource, GraphResource, FileHash, Docs

# alias to latest resource definitions
from dbt.artifacts.resources.v1.components import (
    DependsOn,
    NodeVersion,
    RefArgs,
    HasRelationMetadata,
    ParsedNodeMandatory,
    ParsedNode,
    ColumnInfo,
    CompiledNode,
    InjectedCTE,
    Contract,
    DeferRelation,
    FreshnessThreshold,
    Quoting,
    Time,
)
from dbt.artifacts.resources.v1.manifest_nodes import (
    AnalysisNode,
    HookNode,
    ModelNode,
    SqlNode,
    SeedNode,
    SingularTestNode,
    TestMetadata,
    GenericTestNode,
    SnapshotNode,
)
from dbt.artifacts.resources.v1.documentation import Documentation
from dbt.artifacts.resources.v1.exposure import (
    Exposure,
    ExposureConfig,
    ExposureType,
    MaturityType,
)
from dbt.artifacts.resources.v1.macro import Macro, MacroDependsOn, MacroArgument
from dbt.artifacts.resources.v1.group import Group
from dbt.artifacts.resources.v1.metric import (
    ConstantPropertyInput,
    ConversionTypeParams,
    Metric,
    MetricConfig,
    MetricInput,
    MetricInputMeasure,
    MetricTimeWindow,
    MetricTypeParams,
)
from dbt.artifacts.resources.v1.owner import Owner
from dbt.artifacts.resources.v1.saved_query import (
    Export,
    ExportConfig,
    QueryParams,
    SavedQuery,
    SavedQueryConfig,
    SavedQueryMandatory,
)
from dbt.artifacts.resources.v1.semantic_layer_components import (
    FileSlice,
    SourceFileMetadata,
    WhereFilter,
    WhereFilterIntersection,
)
from dbt.artifacts.resources.v1.semantic_model import (
    Defaults,
    Dimension,
    DimensionTypeParams,
    DimensionValidityParams,
    Entity,
    Measure,
    MeasureAggregationParameters,
    NodeRelation,
    NonAdditiveDimension,
    SemanticModel,
    SemanticModelConfig,
)

from dbt.artifacts.resources.v1.config import (
    NodeAndTestConfig,
    NodeConfig,
    ModelConfig,
    SeedConfig,
    TestConfig,
    SnapshotConfig,
    SourceConfig,
)

from dbt.artifacts.resources.v1.source_definition import (
    ExternalPartition,
    ExternalTable,
    SourceDefinition,
    ParsedSourceMandatory,
)
