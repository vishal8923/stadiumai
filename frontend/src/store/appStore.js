import { create } from 'zustand';

export const useAppStore = create((set, get) => ({
  // User
  userId: localStorage.getItem('stadium_user_id') || null,
  language: localStorage.getItem('stadium_language') || 'en',
  accessibility: {
    voiceMode: localStorage.getItem('stadium_voiceMode') === 'true',
    highContrast: localStorage.getItem('stadium_highContrast') === 'true',
    largeText: localStorage.getItem('stadium_largeText') === 'true',
    wheelchair: localStorage.getItem('stadium_wheelchair') === 'true',
    hearingAssistance: localStorage.getItem('stadium_hearingAssistance') === 'true',
    screenReader: localStorage.getItem('stadium_screenReader') === 'true',
  },
  ticketInfo: {
    section: localStorage.getItem('stadium_section') || '',
    row: localStorage.getItem('stadium_row') || '',
    gate: localStorage.getItem('stadium_gate') || '',
  },

  // Navigation
  currentScreen: 'splash',
  previousScreen: null,
  navHistory: [],

  // Chat
  messages: [],
  isTyping: false,

  // Crowd
  crowdData: {},
  lastCrowdUpdate: null,

  // Notifications
  notifications: [],
  unreadCount: 0,

  // Network
  isOnline: navigator.onLine,
  isSyncing: false,
  pendingActionsCount: 0,

  // Match
  matchData: null,

  // Actions
  setUserId: (id) => {
    localStorage.setItem('stadium_user_id', id);
    set({ userId: id });
  },
  setLanguage: (lang) => {
    localStorage.setItem('stadium_language', lang);
    set({ language: lang });
  },
  toggleAccessibility: (key) =>
    set((state) => {
      const updated = { ...state.accessibility, [key]: !state.accessibility[key] };
      localStorage.setItem(`stadium_${key}`, updated[key]);
      return { accessibility: updated };
    }),
  setAccessibility: (settings) => {
    Object.entries(settings).forEach(([k, v]) => {
      localStorage.setItem(`stadium_${k}`, v);
    });
    set({ accessibility: settings });
  },
  setTicketInfo: (info) => {
    Object.entries(info).forEach(([k, v]) => localStorage.setItem(`stadium_${k}`, v));
    set({ ticketInfo: info });
  },
  navigateTo: (screen) => set((state) => ({
    previousScreen: state.currentScreen,
    currentScreen: screen,
    navHistory: [...state.navHistory, screen],
  })),
  goBack: () => set((state) => {
    const history = [...state.navHistory];
    history.pop();
    const prev = history[history.length - 1] || 'home';
    return { currentScreen: prev, previousScreen: state.currentScreen, navHistory: history };
  }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  clearMessages: () => set({ messages: [] }),
  setTyping: (val) => set({ isTyping: val }),
  setCrowdData: (data) => set({ crowdData: data, lastCrowdUpdate: Date.now() }),
  setNotifications: (notifs) => set({
    notifications: notifs,
    unreadCount: notifs.filter((n) => !n.read).length,
  }),
  markNotificationRead: (id) => set((state) => {
    const updated = state.notifications.map((n) =>
      n.id === id ? { ...n, read: true } : n
    );
    return { notifications: updated, unreadCount: updated.filter((n) => !n.read).length };
  }),
  markAllRead: () => set((state) => ({
    notifications: state.notifications.map((n) => ({ ...n, read: true })),
    unreadCount: 0,
  })),
  setOnline: (val) => set({ isOnline: val }),
  setSyncing: (val) => set({ isSyncing: val }),
  setPendingActionsCount: (count) => set({ pendingActionsCount: count }),
  setMatchData: (data) => set({ matchData: data }),
  resetStore: () => {
    localStorage.clear();
    set({
      userId: null,
      language: 'en',
      accessibility: {
        voiceMode: false, highContrast: false, largeText: false,
        wheelchair: false, hearingAssistance: false, screenReader: false,
      },
      ticketInfo: { section: '', row: '', gate: '' },
      currentScreen: 'onboarding',
      messages: [],
      crowdData: {},
      notifications: [],
    });
  },
}));
