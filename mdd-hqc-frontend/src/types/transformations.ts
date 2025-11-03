export type TransformationMetadata = {
  id: string;
  name: string;
  actor_type: string;
  attributes: Record<string, unknown>;
};

export type TransformationFeature = {
  id: string;
  name: string;
};

export type TransformationRestriction = {
  id: string;
  name: string;
  restriction_type: string;
};

export type TransformationRelation = {
  id: string;
  source: string;
  target: string;
  contribution?: string;
  label?: string;
};

export type CimToPimUvlPayload = {
  metadata: TransformationMetadata[];
  features: {
    primary: TransformationFeature[];
    quality: TransformationFeature[];
  };
  restrictions: TransformationRestriction[];
  relations: TransformationRelation[];
};

export type CimToPimTransformationResponse = {
  model: {
    nodes: Record<string, unknown>[];
    edges: Record<string, unknown>[];
  };
  uvl: CimToPimUvlPayload;
  metrics: {
    istar: import("./metrics").IStarMetrics;
    uvl: import("./metrics").UVLMetrics;
  };
};

export type PimToPsmContextMetrics = {
  featuresCount: number | null;
  tasksCount: number | null;
  resourcesCount: number | null;
};

export type PimToPsmResponse = {
  diagram: string;
  encoded_diagram: string;
  diagram_url: string;
  metrics: {
    architecture: import("./metrics").ArchitectureMetrics;
  };
};
