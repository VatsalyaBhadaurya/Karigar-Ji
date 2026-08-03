import { create } from "zustand";
import { ProjectFull, GarmentSpec, Render } from "@/lib/types";

interface ProjectStore {
  project: ProjectFull | null;
  currentSpec: GarmentSpec | null;
  renders: Render[];
  activeStep: string;
  setProject: (project: ProjectFull) => void;
  setCurrentSpec: (spec: GarmentSpec) => void;
  setRenders: (renders: Render[]) => void;
  updateRender: (render: Render) => void;
  setActiveStep: (step: string) => void;
  reset: () => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  project: null,
  currentSpec: null,
  renders: [],
  activeStep: "upload",

  setProject: (project) => set({ project }),
  setCurrentSpec: (spec) => set({ currentSpec: spec }),
  setRenders: (renders) => set({ renders }),
  updateRender: (render) =>
    set((state) => ({
      renders: state.renders.map((r) => (r.id === render.id ? render : r)),
    })),
  setActiveStep: (step) => set({ activeStep: step }),
  reset: () => set({ project: null, currentSpec: null, renders: [], activeStep: "upload" }),
}));
