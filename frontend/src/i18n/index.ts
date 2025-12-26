import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Lazy load translation resources - only load English initially, others on demand
import en from './locales/en.json';

// Initialize with English only (fast initial load)
const resources = {
  en: { translation: en },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    lng: localStorage.getItem('i18nextLng') || 'en', // Use saved preference or default to English
    debug: false, // Disable debug in production for performance
    
    interpolation: {
      escapeValue: false, // React already does escaping
    },
  });

// Lazy load other languages when needed (non-blocking)
const loadLanguage = async (lang: string) => {
  if (i18n.hasResourceBundle(lang, 'translation')) {
    return; // Already loaded
  }
  
  try {
    switch (lang) {
      case 'es':
        const es = await import('./locales/es.json');
        i18n.addResourceBundle('es', 'translation', es.default);
        break;
      case 'fr':
        const fr = await import('./locales/fr.json');
        i18n.addResourceBundle('fr', 'translation', fr.default);
        break;
      case 'de':
        const de = await import('./locales/de.json');
        i18n.addResourceBundle('de', 'translation', de.default);
        break;
      case 'it':
        const it = await import('./locales/it.json');
        i18n.addResourceBundle('it', 'translation', it.default);
        break;
      case 'pt':
        const pt = await import('./locales/pt.json');
        i18n.addResourceBundle('pt', 'translation', pt.default);
        break;
      case 'nl':
        const nl = await import('./locales/nl.json');
        i18n.addResourceBundle('nl', 'translation', nl.default);
        break;
      case 'ru':
        const ru = await import('./locales/ru.json');
        i18n.addResourceBundle('ru', 'translation', ru.default);
        break;
      case 'ja':
        const ja = await import('./locales/ja.json');
        i18n.addResourceBundle('ja', 'translation', ja.default);
        break;
      case 'zh':
        const zh = await import('./locales/zh.json');
        i18n.addResourceBundle('zh', 'translation', zh.default);
        break;
    }
  } catch (error) {
    console.warn(`Failed to load language ${lang}:`, error);
  }
};

// Preload language when user changes it
i18n.on('languageChanged', (lang) => {
  loadLanguage(lang);
});

export default i18n;
