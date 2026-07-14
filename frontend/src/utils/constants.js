// Stadium Data
export const STADIUM_NAME = 'MetLife Stadium';

// Colors
export const COLORS = {
  bg: '#0A1628',
  surface: '#111D2E',
  pressed: '#070F1A',
  gold: '#FFD700',
  green: '#00C853',
  blue: '#00B4D8',
  red: '#FF3D00',
  orange: '#FF9800',
  yellow: '#FFC107',
  text: '#F0F4F8',
  textSecondary: '#8B9DB8',
  textTertiary: '#4A5D75',
  shadowLight: '#1A2A40',
  shadowDark: '#050A10',
};

// Crowd density levels
export const CROWD_LEVELS = {
  low: { threshold: 0.4, color: '#00C853', opacity: 0.3 },
  medium: { threshold: 0.7, color: '#FFC107', opacity: 0.4 },
  high: { threshold: 0.9, color: '#FF9800', opacity: 0.5 },
  critical: { threshold: 1.0, color: '#FF3D00', opacity: 0.6 },
};

// Sections
export const STADIUM_SECTIONS = Array.from({ length: 32 }, (_, i) => ({
  id: `section_${i + 1}`,
  name: `Section ${i + 1}`,
}));

// Gates
export const STADIUM_GATES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map((g) => ({
  id: `gate_${g.toLowerCase()}`,
  name: `Gate ${g}`,
}));

// Amenities
export const AMENITIES = [
  { id: 'food_north', name: 'Food Court North', type: 'food', x: 30, y: 25 },
  { id: 'food_south', name: 'Food Court South', type: 'food', x: 70, y: 75 },
  { id: 'food_east', name: 'Food Court East', type: 'food', x: 80, y: 40 },
  { id: 'food_west', name: 'Food Court West', type: 'food', x: 20, y: 60 },
  { id: 'restroom_1', name: 'Restroom Block 1', type: 'restroom', x: 25, y: 40 },
  { id: 'restroom_2', name: 'Restroom Block 2', type: 'restroom', x: 75, y: 60 },
  { id: 'restroom_3', name: 'Restroom Block 3', type: 'restroom', x: 50, y: 20 },
  { id: 'restroom_4', name: 'Restroom Block 4', type: 'restroom', x: 50, y: 80 },
  { id: 'medical_1', name: 'Medical Station 1', type: 'medical', x: 40, y: 35 },
  { id: 'medical_2', name: 'Medical Station 2', type: 'medical', x: 60, y: 65 },
  { id: 'info_1', name: 'Info Desk 1', type: 'info', x: 50, y: 50 },
  { id: 'merch_1', name: 'Merchandise Shop', type: 'merch', x: 35, y: 50 },
];

// Languages
export const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸', greeting: 'Hello!' },
  { code: 'es', name: 'Español', flag: '🇪🇸', greeting: '¡Hola!' },
  { code: 'fr', name: 'Français', flag: '🇫🇷', greeting: 'Bonjour!' },
  { code: 'pt', name: 'Português', flag: '🇧🇷', greeting: 'Olá!' },
  { code: 'hi', name: 'हिन्दी', flag: '🇮🇳', greeting: 'नमस्ते!' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦', greeting: 'مرحباً!' },
  { code: 'ja', name: '日本語', flag: '🇯🇵', greeting: 'こんにちは!' },
  { code: 'ko', name: '한국어', flag: '🇰🇷', greeting: '안녕하세요!' },
  { code: 'zh', name: '中文', flag: '🇨🇳', greeting: '你好!' },
];

// Incident types
export const INCIDENT_TYPES = [
  { id: 'medical', label: 'Medical', icon: 'HeartPulse', color: '#FF3D00' },
  { id: 'security', label: 'Security', icon: 'Shield', color: '#FFD700' },
  { id: 'fire', label: 'Fire', icon: 'Flame', color: '#FF3D00' },
  { id: 'lost', label: 'Lost Person', icon: 'UserX', color: '#00B4D8' },
  { id: 'infrastructure', label: 'Infrastructure', icon: 'Wrench', color: '#8B9DB8' },
];

// Severity levels
export const SEVERITY_LEVELS = [
  { value: 1, label: 'Low', color: '#00C853' },
  { value: 2, label: 'Medium', color: '#FFC107' },
  { value: 3, label: 'High', color: '#FF9800' },
  { value: 4, label: 'Critical', color: '#FF3D00' },
];

// Transport modes
export const TRANSPORT_MODES = [
  { id: 'shuttle', name: 'Shuttle Bus', icon: 'Bus', color: '#00B4D8' },
  { id: 'metro', name: 'Metro/Train', icon: 'Train', color: '#00C853' },
  { id: 'taxi', name: 'Taxi/Rideshare', icon: 'Car', color: '#FFD700' },
  { id: 'walking', name: 'Walking', icon: 'Footprints', color: '#8B9DB8' },
  { id: 'parking', name: 'Parking', icon: 'Car', color: '#FF9800' },
];

// Screen names for navigation
export const SCREENS = {
  splash: 'splash',
  onboarding: 'onboarding',
  home: 'home',
  chat: 'chat',
  map: 'map',
  navigation: 'navigation',
  incident: 'incident',
  transport: 'transport',
  accessibility: 'accessibility',
  sustainability: 'sustainability',
  match: 'match',
  dashboard: 'dashboard',
  notifications: 'notifications',
};

// Bottom nav items
export const BOTTOM_NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: 'Home', screen: SCREENS.home },
  { id: 'map', label: 'Map', icon: 'Map', screen: SCREENS.map },
  { id: 'chat', label: 'AI Chat', icon: 'Mic', screen: SCREENS.chat, isCenter: true },
  { id: 'match', label: 'Ticket', icon: 'Ticket', screen: SCREENS.match },
  { id: 'profile', label: 'User', icon: 'User', screen: SCREENS.accessibility },
];

// Quick actions
export const QUICK_ACTIONS = [
  { id: 'navigate', icon: 'Compass', color: '#00B4D8', label: 'Navigate', sublabel: 'To your seat', screen: SCREENS.map },
  { id: 'translate', icon: 'Globe', color: '#FFD700', label: 'Translate', sublabel: '50+ languages', screen: SCREENS.chat },
  { id: 'crowd', icon: 'Users', color: '#00C853', label: 'Crowd Status', sublabel: 'Live density map', screen: SCREENS.map },
  { id: 'report', icon: 'ShieldAlert', color: '#FF3D00', label: 'Report Issue', sublabel: 'Help & safety', screen: SCREENS.incident },
];

// Accessibility options
export const ACCESSIBILITY_OPTIONS = [
  { id: 'voiceMode', label: 'Voice-First Mode', description: 'Navigate the entire app using voice commands' },
  { id: 'highContrast', label: 'High Contrast', description: 'WCAG AAA compliant colors for better visibility' },
  { id: 'largeText', label: 'Large Text', description: '1.5x font scale across all screens' },
  { id: 'wheelchair', label: 'Wheelchair Routing', description: 'Only ramps, elevators, and wide corridors' },
  { id: 'hearingAssistance', label: 'Hearing Assistance', description: 'Visual alerts and captions for all audio' },
  { id: 'screenReader', label: 'Screen Reader', description: 'Enhanced ARIA labels and focus management' },
];

// Mock crowd data
export const MOCK_CROWD_DATA = {
  zones: [
    { zone_id: 'gate_a', density: 0.45, level: 'medium' },
    { zone_id: 'gate_b', density: 0.85, level: 'high' },
    { zone_id: 'gate_c', density: 0.92, level: 'critical' },
    { zone_id: 'gate_d', density: 0.3, level: 'low' },
    { zone_id: 'gate_e', density: 0.55, level: 'medium' },
    { zone_id: 'gate_f', density: 0.2, level: 'low' },
    { zone_id: 'gate_g', density: 0.75, level: 'high' },
    { zone_id: 'gate_h', density: 0.4, level: 'low' },
    { zone_id: 'concourse_1', density: 0.35, level: 'low' },
    { zone_id: 'concourse_2', density: 0.6, level: 'medium' },
    { zone_id: 'section_1', density: 0.8, level: 'high' },
    { zone_id: 'section_2', density: 0.65, level: 'medium' },
    { zone_id: 'section_3', density: 0.5, level: 'medium' },
    { zone_id: 'section_4', density: 0.9, level: 'critical' },
    { zone_id: 'section_5', density: 0.25, level: 'low' },
    { zone_id: 'section_6', density: 0.7, level: 'high' },
    { zone_id: 'section_7', density: 0.45, level: 'medium' },
    { zone_id: 'section_8', density: 0.35, level: 'low' },
    { zone_id: 'food_north', density: 0.88, level: 'high' },
    { zone_id: 'food_south', density: 0.55, level: 'medium' },
    { zone_id: 'restroom_1', density: 0.78, level: 'high' },
    { zone_id: 'restroom_2', density: 0.42, level: 'low' },
  ],
  timestamp: new Date().toISOString(),
};

// Mock match data
export const MOCK_MATCH_DATA = {
  home_team: { name: 'USA', code: 'US', flag: '🇺🇸', score: 2 },
  away_team: { name: 'BRA', code: 'BR', flag: '🇧🇷', score: 1 },
  status: 'live',
  minute: 72,
  second: 14,
  stadium: 'MetLife Stadium',
  venue: 'Section 12B',
  possession: { home: 55, away: 45 },
  events: [
    { time: '12:34', type: 'goal', team: 'home', player: 'Pulisic', description: 'Goal! USA takes the lead' },
    { time: '28:15', type: 'yellow', team: 'away', player: 'Neymar', description: 'Yellow card for dissent' },
    { time: '45:00', type: 'halftime', description: 'Halftime: USA 1-0 BRA' },
    { time: '52:22', type: 'goal', team: 'away', player: 'Vinicius Jr', description: 'Equalizer for Brazil!' },
    { time: '68:05', type: 'goal', team: 'home', player: 'Weah', description: 'USA retakes the lead!' },
    { time: '70:30', type: 'substitution', team: 'home', description: 'Substitution for USA' },
  ],
  stats: {
    shots: { home: 12, away: 8 },
    passes: { home: 340, away: 290 },
    fouls: { home: 8, away: 11 },
    corners: { home: 5, away: 3 },
    offsides: { home: 2, away: 1 },
  },
};

// Mock chat responses
export const MOCK_CHAT_RESPONSES = {
  food: {
    response_text: 'Try Food Court North — 3 min walk, 5 min wait. Route: Gate A → Concourse 1 → Food Court North. They have burgers, pizza, and vegetarian options.',
    actions: [{ type: 'navigate', to: 'food_court_north' }],
    route: { estimated_time: 3, distance: 150 },
  },
  seat: {
    response_text: 'Head to Gate A, take the left corridor, elevator to Level 2. Your seat is 5 rows up on the right. Estimated 8 min walk.',
    actions: [{ type: 'navigate', to: 'sec_12b' }],
    route: { estimated_time: 8, distance: 450 },
  },
  crowd: {
    response_text: 'Gate C is currently at 92% capacity (CRITICAL). I recommend using Gate D instead — only 30% capacity and 5 min faster.',
    actions: [{ type: 'navigate', to: 'gate_d' }],
    route: { estimated_time: 5, distance: 200 },
  },
  help: {
    response_text: 'I can help you with: navigation, crowd info, food locations, transport, incident reporting, and translations. What do you need?',
    actions: [],
  },
  hello: {
    response_text: 'Hello! Welcome to StadiumAI. I am your AI companion for the FIFA World Cup 2026. How can I assist you today?',
    actions: [],
  },
  default: {
    response_text: 'I understand. Let me help you with that. You can ask me about navigation, crowd levels, food options, or report an incident.',
    actions: [],
  },
};

// Transport options
export const MOCK_TRANSPORT_OPTIONS = [
  { id: 'shuttle_1', mode: 'shuttle', name: 'Shuttle Bus - Route A', eta: 12, status: 'on_time', distance: 50, crowd_level: 'medium', carbon_saved: 0.8, recommended: true },
  { id: 'metro_1', mode: 'metro', name: 'Metro Line 1', eta: 8, status: 'crowded', distance: 200, crowd_level: 'high', carbon_saved: 1.2, recommended: false },
  { id: 'taxi_1', mode: 'taxi', name: 'Taxi Stand', eta: 18, status: 'available', distance: 100, crowd_level: 'low', carbon_saved: 0, recommended: false },
  { id: 'walking_1', mode: 'walking', name: 'Walking Route', eta: 25, status: 'clear', distance: 0, crowd_level: 'low', carbon_saved: 1.5, recommended: false },
];
