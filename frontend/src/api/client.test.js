import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchStyles, fetchTranslation } from './client'

const API_BASE = 'http://localhost:8000'

function mockFetch(response) {
  const spy = vi.fn().mockResolvedValue(response)
  vi.stubGlobal('fetch', spy)
  return spy
}

function ok(body) {
  return { ok: true, json: async () => body }
}

function fail(body) {
  return { ok: false, json: async () => body }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('fetchStyles', () => {
  it('성공 시 스타일 맵을 그대로 반환한다', async () => {
    const styles = { general: '일반체', sns: 'SNS체' }
    const spy = mockFetch(ok(styles))

    await expect(fetchStyles()).resolves.toEqual(styles)
    expect(spy).toHaveBeenCalledWith(`${API_BASE}/styles`)
  })

  it('실패 시 에러를 던진다', async () => {
    mockFetch(fail({}))

    await expect(fetchStyles()).rejects.toThrow('스타일 목록을 불러오지 못했습니다.')
  })
})

describe('fetchTranslation', () => {
  it('target_lang으로 snake_case 변환해서 POST한다', async () => {
    const spy = mockFetch(ok({ translated: '결과', style: 'sns' }))

    await fetchTranslation({ text: '안녕', targetLang: '영어', style: 'sns' })

    const [url, options] = spy.mock.calls[0]
    expect(url).toBe(`${API_BASE}/translate`)
    expect(options.method).toBe('POST')
    expect(options.headers['Content-Type']).toBe('application/json')
    expect(JSON.parse(options.body)).toEqual({
      text: '안녕',
      target_lang: '영어',
      style: 'sns',
    })
  })

  it('성공 시 응답 본문을 반환한다', async () => {
    mockFetch(ok({ translated: '결과', style: 'general' }))

    await expect(
      fetchTranslation({ text: '안녕', targetLang: '한국어', style: 'general' }),
    ).resolves.toEqual({ translated: '결과', style: 'general' })
  })

  // 백엔드 에러 응답 형식({"detail": ...})에 의존하는 테스트.
  // 공통 예외처리 리팩토링 시 client.js와 함께 여기도 수정해야 합니다.
  it('실패 시 백엔드의 detail 메시지를 에러로 던진다', async () => {
    mockFetch(fail({ detail: '알 수 없는 스타일: xxx' }))

    await expect(
      fetchTranslation({ text: '안녕', targetLang: '한국어', style: 'xxx' }),
    ).rejects.toThrow('알 수 없는 스타일: xxx')
  })

  it('detail이 없으면 기본 메시지로 대체한다', async () => {
    mockFetch(fail({}))

    await expect(
      fetchTranslation({ text: '안녕', targetLang: '한국어', style: 'general' }),
    ).rejects.toThrow('번역 요청이 실패했습니다.')
  })

  it('본문이 JSON이 아니어도 기본 메시지로 처리한다', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => {
          throw new Error('not json')
        },
      }),
    )

    await expect(
      fetchTranslation({ text: '안녕', targetLang: '한국어', style: 'general' }),
    ).rejects.toThrow('번역 요청이 실패했습니다.')
  })
})
