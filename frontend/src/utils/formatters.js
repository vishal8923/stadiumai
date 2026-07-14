export const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatRelativeTime = (date) => {
  const now = new Date();
  const then = new Date(date);
  const diff = Math.floor((now - then) / 1000);

  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
  return `${Math.floor(diff / 86400)} days ago`;
};

export const formatMatchTime = (minute, second) => {
  return `${minute.toString().padStart(2, '0')}:${second.toString().padStart(2, '0')}`;
};

export const formatNumber = (num) => {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

export const getDensityColor = (density) => {
  if (density < 0.4) return '#00C853';
  if (density < 0.7) return '#FFC107';
  if (density < 0.9) return '#FF9800';
  return '#FF3D00';
};

export const getDensityLabel = (density) => {
  if (density < 0.4) return 'Low';
  if (density < 0.7) return 'Medium';
  if (density < 0.9) return 'High';
  return 'Critical';
};

export const getLanguageCode = (lang) => {
  const map = {
    en: 'en-US', es: 'es-ES', fr: 'fr-FR', pt: 'pt-BR',
    hi: 'hi-IN', ar: 'ar-SA', ja: 'ja-JP', ko: 'ko-KR', zh: 'zh-CN',
  };
  return map[lang] || 'en-US';
};

export const truncate = (str, maxLength) => {
  if (!str || str.length <= maxLength) return str;
  return str.substring(0, maxLength) + '...';
};
