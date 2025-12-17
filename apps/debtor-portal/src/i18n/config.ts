/**
 * i18n Configuration for Debtor Portal
 * Multilingual support from day 1
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslations from './locales/en.json';
import roTranslations from './locales/ro.json';
import csTranslations from './locales/cs.json';

i18n
  .use(LanguageDetector) // Detects language from browser
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslations,
      },
      ro: {
        translation: roTranslations,
      },
      cs: {
        translation: csTranslations,
      },
    },
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false, // React already escapes
    },
    detection: {
      // Order of language detection:
      // 1. Session storage (manual override)
      // 2. Browser language
      // 3. Fallback to 'en'
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'debtor_portal_language',
    },
  });

export default i18n;

