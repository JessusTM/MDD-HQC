import { useState } from "react";

import { Layout } from "../Layout/Layout";
import { LevelFilter } from "../Filters/LevelFilter";
import { MetricsPanel } from "../Metrics/MetricsPanel";
import { CimLevel } from "../Levels/CimLevel";
import { PimLevel } from "../Levels/PimLevel";
import { PsmLevel } from "../Levels/PsmLevel";
import type { LevelKey } from "../../types/levels";
import type {
  ArchitectureMetrics,
  IStarMetrics,
  MetricsState,
  UVLMetrics,
} from "../../types/metrics";
import type { PimToPsmContextMetrics } from "../../types/transformations";
import { transformCimToPim } from "../../services/CimService";
import { transformPimToPsm } from "../../services/PimService";
import { formatUvlContent } from "../../utils/uvl";

const emptyIStarMetrics: IStarMetrics = {
  transformationTimeMs: null,
  goalsCount: null,
  softgoalsCount: null,
  resourcesCount: null,
  tasksCount: null,
};

const emptyUVLMetrics: UVLMetrics = {
  transformationTimeMs: null,
  featuresCount: null,
  constraintsCount: null,
  goalsConvertedPercent: null,
  semanticLossPercent: null,
};

const emptyArchitectureMetrics: ArchitectureMetrics = {
  transformationTimeMs: null,
  classesCount: null,
  attributesCount: null,
  methodsCount: null,
  featuresToClassesPercent: null,
  tasksToMethodsPercent: null,
  resourcesToAttributesPercent: null,
  semanticLossPercent: null,
};

const buildEmptyMetrics = (): MetricsState => ({
  istar: { ...emptyIStarMetrics },
  uvl: { ...emptyUVLMetrics },
  architecture: { ...emptyArchitectureMetrics },
});

const buildContextMetrics = (metrics: MetricsState): PimToPsmContextMetrics => ({
  featuresCount: metrics.uvl.featuresCount,
  tasksCount: metrics.istar.tasksCount,
  resourcesCount: metrics.istar.resourcesCount,
});

export const Orchestrator = () => {
  const [fromLevel, setFromLevel] = useState<LevelKey>("cim");
  const [toLevel, setToLevel] = useState<LevelKey>("pim");
  const [uploadedXml, setUploadedXml] = useState<string | null>(null);
  const [uvlContent, setUvlContent] = useState<string>("");
  const [plantUmlSource, setPlantUmlSource] = useState<string>("");
  const [plantUmlImageUrl, setPlantUmlImageUrl] = useState<string>("");
  const [isTransforming, setIsTransforming] = useState(false);
  const [activeTransform, setActiveTransform] = useState<"cim-pim" | "pim-psm" | null>(null);
  const [pimError, setPimError] = useState<string | null>(null);
  const [psmError, setPsmError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<MetricsState>(buildEmptyMetrics());

  const resetForNewModel = () => {
    setUvlContent("");
    setPlantUmlSource("");
    setPlantUmlImageUrl("");
    setPimError(null);
    setPsmError(null);
    setFromLevel("cim");
    setToLevel("pim");
    setMetrics(buildEmptyMetrics());
  };

  const handleModelReady = (xml: string) => {
    setUploadedXml(xml);
    resetForNewModel();
  };

  const handleModelCleared = () => {
    setUploadedXml(null);
    resetForNewModel();
  };

  const handleTransform = async () => {
    const transition =
      fromLevel === "cim" && toLevel === "pim"
        ? "cim-pim"
        : fromLevel === "pim" && toLevel === "psm"
        ? "pim-psm"
        : null;

    if (!transition) {
      setPsmError("Transformación no soportada actualmente.");
      return;
    }

    setActiveTransform(transition);
    setIsTransforming(true);
    setPimError(null);
    setPsmError(null);

    try {
      if (transition === "cim-pim") {
        if (!uploadedXml) {
          setPimError("Debe cargar un modelo i* antes de transformar.");
          return;
        }

        const response = await transformCimToPim(uploadedXml);
        const uvlText = formatUvlContent(response.uvl);

        setUvlContent(uvlText);
        setPlantUmlSource("");
        setPlantUmlImageUrl("");
        setMetrics({
          istar: response.metrics.istar,
          uvl: response.metrics.uvl,
          architecture: { ...emptyArchitectureMetrics },
        });
        setFromLevel("pim");
        setToLevel("psm");
      } else if (transition === "pim-psm") {
        if (!uvlContent.trim()) {
          setPsmError("Debe generar el UVL antes de obtener la arquitectura.");
          return;
        }

        const contextMetrics = buildContextMetrics(metrics);
        const response = await transformPimToPsm(uvlContent, contextMetrics);

        setPlantUmlSource(response.diagram);
        setPlantUmlImageUrl(response.diagram_url);
        setMetrics((previous) => ({
          ...previous,
          architecture: response.metrics.architecture,
        }));
      }
    } catch (error) {
      console.error("No se pudo transformar el modelo", error);
      if (fromLevel === "cim") {
        setPimError("No se pudo transformar el modelo. Intente nuevamente.");
      } else {
        setPsmError("No se pudo generar la arquitectura. Intente nuevamente.");
      }
    } finally {
      setIsTransforming(false);
      setActiveTransform(null);
    }
  };

  const isTransformDisabled =
    isTransforming ||
    (fromLevel === "cim" && !uploadedXml) ||
    (fromLevel === "pim" && !uvlContent.trim());

  return (
    <Layout>
      <section className="row g-4">
        <div className="col-md-4">
          <CimLevel onModelReady={handleModelReady} onModelCleared={handleModelCleared} />
        </div>
        <div className="col-md-4">
          <PimLevel
            content={uvlContent}
            isTransforming={isTransforming && activeTransform === "cim-pim"}
            errorMessage={pimError}
          />
        </div>
        <div className="col-md-4">
          <PsmLevel
            diagramUrl={plantUmlImageUrl}
            plantUmlSource={plantUmlSource}
            isTransforming={isTransforming && activeTransform === "pim-psm"}
            errorMessage={psmError}
          />
        </div>
      </section>

      <MetricsPanel metrics={metrics} />

      <LevelFilter
        from={fromLevel}
        to={toLevel}
        onFromChange={setFromLevel}
        onToChange={setToLevel}
        onTransform={handleTransform}
        isTransforming={isTransforming}
        isTransformDisabled={isTransformDisabled}
      />
    </Layout>
  );
};
