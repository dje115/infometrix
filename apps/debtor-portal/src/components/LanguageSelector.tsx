/**
 * Language Selector Component
 * 
 * Allows users to manually override language selection.
 * Auto-detects from browser, session, or API.
 */

import React from 'react'
import { useTranslation } from 'react-i18next'
import { Select, MenuItem, FormControl, InputLabel, SelectChangeEvent } from '@mui/material'
import LanguageIcon from '@mui/icons-material/Language'

const LanguageSelector: React.FC = () => {
  const { i18n } = useTranslation()

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ro', name: 'Română' },
    { code: 'cs', name: 'Čeština' },
  ]

  const handleLanguageChange = (event: SelectChangeEvent<string>) => {
    const newLang = event.target.value
    i18n.changeLanguage(newLang)
    
    // Persist to localStorage
    localStorage.setItem('debtor_portal_language', newLang)
    sessionStorage.setItem('debtor_portal_language', newLang)
  }

  return (
    <FormControl size="small" sx={{ minWidth: 120 }}>
      <InputLabel id="language-select-label">
        <LanguageIcon sx={{ fontSize: 18, mr: 0.5, verticalAlign: 'middle' }} />
        Language
      </InputLabel>
      <Select
        labelId="language-select-label"
        value={i18n.language}
        onChange={handleLanguageChange}
        label="Language"
      >
        {languages.map((lang) => (
          <MenuItem key={lang.code} value={lang.code}>
            {lang.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  )
}

export default LanguageSelector



