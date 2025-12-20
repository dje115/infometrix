/**
 * i18n Configuration for Debtor Portal
 * 
 * Multilingual support from day 1.
 * Language detection order:
 * 1. Session preferred language (if token includes it)
 * 2. Debtor preferred language from API
 * 3. Browser language
 * 4. Fallback: 'en'
 */

import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import enTranslations from './locales/en.json'
import roTranslations from './locales/ro.json'
import csTranslations from './locales/cs.json'

// Detect language from various sources
const detectLanguage = (): string => {
  // 1. Check session storage (set by login/token)
  const sessionLang = sessionStorage.getItem('debtor_portal_language')
  if (sessionLang) {
    return sessionLang
  }
  
  // 2. Check localStorage (persisted preference)
  const storedLang = localStorage.getItem('debtor_portal_language')
  if (storedLang) {
    return storedLang
  }
  
  // 3. Check browser language
  const browserLang = navigator.language.split('-')[0]
  if (['en', 'ro', 'cs'].includes(browserLang)) {
    return browserLang
  }
  
  // 4. Fallback to English
  return 'en'
}

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: enTranslations
      },
      ro: {
        translation: roTranslations
      },
      cs: {
        translation: csTranslations
      }
    },
    lng: detectLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  })

export default i18n



