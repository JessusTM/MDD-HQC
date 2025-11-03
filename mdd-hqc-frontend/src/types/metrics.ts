export type NullableMetricValue = number | null;

export type IStarMetrics = {
  transformationTimeMs: NullableMetricValue;
  goalsCount: NullableMetricValue;
  softgoalsCount: NullableMetricValue;
  resourcesCount: NullableMetricValue;
  tasksCount: NullableMetricValue;
};

export type UVLMetrics = {
  transformationTimeMs: NullableMetricValue;
  featuresCount: NullableMetricValue;
  constraintsCount: NullableMetricValue;
  goalsConvertedPercent: NullableMetricValue;
  semanticLossPercent: NullableMetricValue;
};

export type ArchitectureMetrics = {
  transformationTimeMs: NullableMetricValue;
  classesCount: NullableMetricValue;
  attributesCount: NullableMetricValue;
  methodsCount: NullableMetricValue;
  featuresToClassesPercent: NullableMetricValue;
  tasksToMethodsPercent: NullableMetricValue;
  resourcesToAttributesPercent: NullableMetricValue;
  semanticLossPercent: NullableMetricValue;
};

export type MetricsState = {
  istar: IStarMetrics;
  uvl: UVLMetrics;
  architecture: ArchitectureMetrics;
};

export type MetricsPanelProps = {
  metrics: MetricsState;
};

export type MetricRowProps = {
  label: string;
  value: string;
  isLast?: boolean;
};
