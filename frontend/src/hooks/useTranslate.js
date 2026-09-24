import { useState } from 'react'
import { fetchTranslation } from '../api/client'

export function useTranslate() {
  const [candidates, setCandidates] = useState([])
  const [selected, setSelected] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function translate({ text, targetLang, style }) {
    if (!text.trim()) {
      setError('번역할 문장을 입력해 주세요.')
      return
    }
    setLoading(true)
    setError('')
    setCandidates([])
    setSelected(0)
    try {
      const data = await fetchTranslation({ text, targetLang, style })
      setCandidates(data.candidates)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return { candidates, selected, setSelected, loading, error, translate }
}
