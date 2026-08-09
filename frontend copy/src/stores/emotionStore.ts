import { create } from 'zustand';

export interface Emotion {
  name: string;
  percentage: number;
  color: string;
}

export interface EmotionState {
  isScanning: boolean;
  hasScanned: boolean;
  emotions: Emotion[];
  selectedChoice: 'amplify' | 'transition' | null;
  
  // Actions
  startScanning: () => void;
  completeScanning: (emotions: Emotion[]) => void;
  setChoice: (choice: 'amplify' | 'transition') => void;
  resetState: () => void;
}

const mockEmotions: Emotion[] = [
  { name: 'Happy', percentage: 70, color: 'hsl(195 100% 50%)' },
  { name: 'Neutral', percentage: 10, color: 'hsl(0 0% 65%)' },
  { name: 'Surprised', percentage: 5, color: 'hsl(300 100% 50%)' },
  { name: 'Sad', percentage: 15, color: 'hsl(220 100% 45%)' },
];

export const useEmotionStore = create<EmotionState>((set) => ({
  isScanning: false,
  hasScanned: false,
  emotions: [],
  selectedChoice: null,

  startScanning: () => set({ isScanning: true }),
  
  completeScanning: (emotions: Emotion[]) => 
    set({ 
      isScanning: false, 
      hasScanned: true, 
      emotions: emotions.length > 0 ? emotions : mockEmotions 
    }),
  
  setChoice: (choice: 'amplify' | 'transition') => 
    set({ selectedChoice: choice }),
  
  resetState: () => 
    set({ 
      isScanning: false, 
      hasScanned: false, 
      emotions: [], 
      selectedChoice: null 
    }),
}));