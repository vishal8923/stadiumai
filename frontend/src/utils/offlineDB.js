import { get, set, del } from 'idb-keyval';

const DB_KEYS = {
  USER_PROFILE: 'stadium_user_profile',
  LANGUAGE: 'stadium_language',
  ACCESSIBILITY: 'stadium_accessibility',
  TICKET_INFO: 'stadium_ticket_info',
  LAST_ROUTE: 'stadium_last_route',
  RECENT_MAPS: 'stadium_recent_maps',
  CROWD_DATA: 'stadium_crowd_data',
  MATCH_DATA: 'stadium_match_data',
  ACCESSIBILITY_DATA: 'stadium_accessibility_data',
  EMERGENCY_EXITS: 'stadium_emergency_exits',
  PENDING_ACTIONS: 'stadium_pending_actions',
  OFFLINE_MESSAGES: 'stadium_offline_messages',
};

export const saveUserProfile = (profile) => set(DB_KEYS.USER_PROFILE, profile);
export const getUserProfile = () => get(DB_KEYS.USER_PROFILE);

export const saveLanguage = (lang) => set(DB_KEYS.LANGUAGE, lang);
export const getLanguage = async () => (await get(DB_KEYS.LANGUAGE)) || 'en';

export const saveAccessibility = (settings) => set(DB_KEYS.ACCESSIBILITY, settings);
export const getAccessibility = async () => (await get(DB_KEYS.ACCESSIBILITY)) || {
  voiceMode: false, highContrast: false, largeText: false,
  wheelchair: false, hearingAssistance: false, screenReader: false,
};

export const saveTicketInfo = (info) => set(DB_KEYS.TICKET_INFO, info);
export const getTicketInfo = () => get(DB_KEYS.TICKET_INFO);

export const saveLastRoute = (route) => set(DB_KEYS.LAST_ROUTE, route);
export const getLastRoute = () => get(DB_KEYS.LAST_ROUTE);

export const saveRecentMap = (mapData) => {
  get(DB_KEYS.RECENT_MAPS).then((maps) => {
    const updated = [mapData, ...(maps || [])].slice(0, 10);
    set(DB_KEYS.RECENT_MAPS, updated);
  });
};
export const getRecentMaps = async () => (await get(DB_KEYS.RECENT_MAPS)) || [];

export const saveCrowdData = (data) => set(DB_KEYS.CROWD_DATA, { data, timestamp: Date.now() });
export const getCrowdData = () => get(DB_KEYS.CROWD_DATA);

export const saveMatchData = (data) => set(DB_KEYS.MATCH_DATA, { data, timestamp: Date.now() });
export const getMatchData = () => get(DB_KEYS.MATCH_DATA);

export const saveAccessibilityData = (data) => set(DB_KEYS.ACCESSIBILITY_DATA, { data, timestamp: Date.now() });
export const getAccessibilityData = () => get(DB_KEYS.ACCESSIBILITY_DATA);

export const saveEmergencyExits = (data) => set(DB_KEYS.EMERGENCY_EXITS, data);
export const getEmergencyExits = () => get(DB_KEYS.EMERGENCY_EXITS);

export const addPendingAction = (action) => {
  get(DB_KEYS.PENDING_ACTIONS).then((actions) => {
    set(DB_KEYS.PENDING_ACTIONS, [...(actions || []), { ...action, id: crypto.randomUUID(), timestamp: Date.now() }]);
  });
};
export const getPendingActions = async () => (await get(DB_KEYS.PENDING_ACTIONS)) || [];
export const removePendingAction = (id) => {
  get(DB_KEYS.PENDING_ACTIONS).then((actions) => {
    set(DB_KEYS.PENDING_ACTIONS, (actions || []).filter((a) => a.id !== id));
  });
};
export const clearPendingActions = () => del(DB_KEYS.PENDING_ACTIONS);

export const saveOfflineMessage = (msg) => {
  get(DB_KEYS.OFFLINE_MESSAGES).then((msgs) => {
    set(DB_KEYS.OFFLINE_MESSAGES, [...(msgs || []), msg]);
  });
};
export const getOfflineMessages = async () => (await get(DB_KEYS.OFFLINE_MESSAGES)) || [];
export const clearOfflineMessages = () => del(DB_KEYS.OFFLINE_MESSAGES);
