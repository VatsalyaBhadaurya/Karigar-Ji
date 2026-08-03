import { create } from "zustand";

interface GenerationState {
  status: "idle" | "loading" | "complete" | "error";
  message?: string;
}

interface UiStore {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;

  generationStates: Record<string, GenerationState>;
  setGenerationState: (key: string, state: GenerationState) => void;

  activeModal: string | null;
  setActiveModal: (modal: string | null) => void;
}

export const useUiStore = create<UiStore>((set) => ({
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  generationStates: {},
  setGenerationState: (key, state) =>
    set((prev) => ({ generationStates: { ...prev.generationStates, [key]: state } })),

  activeModal: null,
  setActiveModal: (modal) => set({ activeModal: modal }),
}));
