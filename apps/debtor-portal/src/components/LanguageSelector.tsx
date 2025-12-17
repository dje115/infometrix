/**
 * Language Selector Component
 * Allows manual language override
 */

import React from 'react';
import { Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'ro', name: 'Română' },
  { code: 'cs', name: 'Čeština' },
];

const LanguageSelector: React.FC = () => {
  const { i18n } = useTranslation();

  const handleLanguageChange = (event: any) => {
    const language = event.target.value;
    i18n.changeLanguage(language);
    // Store in session storage for persistence
    localStorage.setItem('debtor_portal_language', language);
  };

  return (
    <FormControl size="small" sx={{ minWidth: 120 }}>
      <InputLabel>Language</InputLabel>
      <Select
        value={i18n.language}
        label="Language"
        onChange={handleLanguageChange}
      >
        {languages.map((lang) => (
          <MenuItem key={lang.code} value={lang.code}>
            {lang.name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default LanguageSelector;

