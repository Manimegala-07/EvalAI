import { createContext, useContext, useState } from "react";
import TRANSLATIONS from "../constants/translations";

const LangContext = createContext(null);
export function useLang() { return useContext(LangContext); }

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem("evalai_lang") || "en");

  const setLanguage = (code) => {
    setLang(code);
    localStorage.setItem("evalai_lang", code);
  };

  const t = (key, vars = {}) => {
    const str = TRANSLATIONS[lang]?.[key] || TRANSLATIONS["en"]?.[key] || key;
    return str.replace(/\{(\w+)\}/g, (_, k) => vars[k] || k);
  };

  return (
    <LangContext.Provider value={{ lang, setLanguage, t }}>
      {children}
    </LangContext.Provider>
  );
}
