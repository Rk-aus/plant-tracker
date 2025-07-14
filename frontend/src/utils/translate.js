import axios from 'axios';

const ENDPOINT = 'https://libretranslate.de/translate';
const CACHE_PREFIX = 'loc_ja_';

export async function translateToJa(text) {
  const cached = localStorage.getItem(CACHE_PREFIX + text);
  if (cached) {
    return cached;
  }

  try {
    const { data } = await axios.post(
      ENDPOINT,
      { q: text, source: 'en', target: 'ja', format: 'text' },
      { headers: { accept: 'application/json' } }
    );
    localStorage.setItem(CACHE_PREFIX + text, data.translatedText);
    return data.translatedText;
  } catch (e) {
    console.error('Translation failed:', e);
    return text;
  }
}
