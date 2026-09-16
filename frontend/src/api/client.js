const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

// 백엔드는 모든 응답을 { success, data } / { success, error: { code, message } }로 감싸서 보냅니다.
// 이 함수가 그 껍데기를 벗겨내므로, 이 파일 밖에서는 응답 형식을 몰라도 됩니다.
async function unwrap(res, fallbackMessage) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const error = new Error(body.error?.message || fallbackMessage)
    error.code = body.error?.code
    throw error
  }
  const body = await res.json()
  return body.data
}

export async function fetchStyles() {
  const res = await fetch(`${API_BASE}/styles`)
  return unwrap(res, '스타일 목록을 불러오지 못했습니다.')
}

export async function fetchTranslation({ text, targetLang, style }) {
  const res = await fetch(`${API_BASE}/translate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, target_lang: targetLang, style }),
  })
  return unwrap(res, '번역 요청이 실패했습니다.')
}
