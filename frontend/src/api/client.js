const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

export async function fetchStyles() {
  const res = await fetch(`${API_BASE}/styles`)
  if (!res.ok) throw new Error('스타일 목록을 불러오지 못했습니다.')
  return res.json()
}

export async function fetchTranslation({ text, targetLang, style }) {
  const res = await fetch(`${API_BASE}/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, target_lang: targetLang, style }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || '번역 요청이 실패했습니다.')
  }
  return res.json()
}
