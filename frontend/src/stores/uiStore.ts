/* Zustand UI store for managing UI state. */

import { create } from 'zustand';

export interface UIStore {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  darkMode: boolean;
  setDarkMode: (dark: boolean) => void;
  loading: boolean;
  setLoading: (loading: boolean) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  darkMode: false,
  setDarkMode: (dark) => {
    localStorage.setItem('darkMode', JSON.stringify(dark));
    set({ darkMode: dark });
  },

  loading: false,
  setLoading: (loading) => set({ loading }),
}));
