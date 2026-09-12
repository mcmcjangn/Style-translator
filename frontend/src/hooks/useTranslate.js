import { useState } from 'react'
import { fetchTranslation } from '../api/client'

export function useTranslate() {
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function translate({ text, targetLang, style }) {
    if (!text.trim()) {
      setError('번역할 문장을 입력해 주세요.')
      return
    }
    setLoading(true)
    setError('')
    setResult('')
    try {
      const data = await fetchTranslation({ text, targetLang, style })
      setResult(data.translated)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, translate }
}
