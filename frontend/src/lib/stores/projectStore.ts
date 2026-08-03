import { create } from "zustand";
import { ProjectFull, GarmentSpec, GarmentSpecRow, Render } from "@/lib/types";

interface ProjectStore {
  project: ProjectFull | null;
  currentSpec: GarmentSpec | null;
  currentSpecRow: GarmentSpecRow | null;
  renders: Render[];
  activeStep: string;
  setProject: (project: ProjectFull) => void;
  setCurrentSpec: (spec: GarmentSpec) => void;
  setCurrentSpecRow: (row: GarmentSpecRow) => void;
  setRenders: (renders: Render[]) => void;
  updateRender: (render: Render) => void;
  setActiveStep: (step: string) => void;
  reset: () => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  project: null,
  currentSpec: null,
  currentSpecRow: null,
  renders: [],
  activeStep: "upload",

  setProject: (project) => set({ project }),
  setCurrentSpec: (spec) => set({ currentSpec: spec }),
  setCurrentSpecRow: (row) => set({ currentSpecRow: row, currentSpec: row.spec_json }),
  setRenders: (renders) => set({ renders }),
  updateRender: (render) =>
    set((state) => ({
      renders: state.renders.map((r) => (r.id === render.id ? render : r)),
    })),
  setActiveStep: (step) => set({ activeStep: step }),
  reset: () => set({ project: null, currentSpec: null, currentSpecRow: null, renders: [], activeStep: "upload" }),
}));
