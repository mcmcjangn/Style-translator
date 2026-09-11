import { useEffect, useState } from 'react'
import './App.css'

<App className="css"></App>
const API_BASE = 'http://localhost:8000'

const FALLBACK_STYLES = {
  general: '일반체',
  formal: '격식체 (해요체)',
  sns: 'SNS체 (대화체)',
}

const LANGUAGES = [
  { code: 'en', label: '영어' },
  { code: 'ko', label: '한국어' },
  { code: 'ja', label: '일본어' },
  { code: 'zh', label: '중국어' },
]

export default function App() {
  const [styles, setStyles] = useState(FALLBACK_STYLES)
  const [text, setText] = useState('')
  const [targetLang, setTargetLang] = useState('en')
  const [style, setStyle] = useState('general')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API_BASE}/styles`)
      .then((res) => res.json())
      .then(setStyles)
      .catch(() => {})
  }, [])

  async function handleTranslate() {
    if (!text.trim()) {
      setError('번역할 문장을 입력해 주세요.')
      return
    }
    setLoading(true)
    setError('')
    setResult('')
    try {
      const res = await fetch(`${API_BASE}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, target_lang: targetLang, style }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || '번역 요청이 실패했습니다.')
      }
      const data = await res.json()
      setResult(data.translated)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="page__header">
        <span className="eyebrow">STYLE TRANSLATOR — BETA</span>
        <h1>AI Translator</h1>
        <p className="subtitle">문장을 넣고 스타일을 고르면, 그 말투로 다시 바꿔 드립니다.</p>
      </header>

      <main className="panel">
        <textarea
          className="input-area"
          placeholder="문장을 입력하세요"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
        />

        <div className="controls">
          <div className="control">
            <label htmlFor="lang">언어</label>
            <select id="lang" value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
              {LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>

          <div className="control">
            <label htmlFor="style">스타일</label>
            <select id="style" value={style} onChange={(e) => setStyle(e.target.value)}>
              {Object.entries(styles).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <button className="translate-btn" onClick={handleTranslate} disabled={loading}>
            {loading ? '변환 중…' : '변환하기'}
          </button>
        </div>

        {error && <p className="error" role="alert">{error}</p>}

        {result && (
          <div className="result">
            <span className="result__label">결과 · {styles[style] ?? style}</span>
            <p className="result__text">{result}</p>
          </div>
        )}
      </main>

      <footer className="page__footer">
        <span>백엔드: FastAPI + Gemini API</span>
      </footer>
    </div>
  )
}