import { http, HttpResponse } from 'msw'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const handlers = [
  // Auth endpoints
  http.post(`${API_BASE_URL}/api/auth/login`, async ({ request }) => {
    const body = await request.json() as { email: string; password: string }

    if (body.email === 'test@example.com' && body.password === 'password123') {
      return HttpResponse.json({
        access_token: 'mock-jwt-token',
        token_type: 'bearer',
      })
    }

    return HttpResponse.json(
      { detail: 'Incorrect email or password' },
      { status: 401 }
    )
  }),

  http.post(`${API_BASE_URL}/api/auth/register`, async ({ request }) => {
    const body = await request.json()

    // Check if user already exists
    if (body.email === 'existing@example.com') {
      return HttpResponse.json(
        { detail: 'Email already registered' },
        { status: 400 }
      )
    }

    return HttpResponse.json({
      id: '1',
      email: body.email,
      full_name: body.full_name,
    })
  }),

  http.get(`${API_BASE_URL}/api/v1/auth/me`, () => {
    return HttpResponse.json({
      id: '1',
      email: 'test@example.com',
      full_name: 'Test User',
    })
  }),

  // Dashboard stats endpoints
  http.get(`${API_BASE_URL}/api/dashboard/stats`, () => {
    return HttpResponse.json({
      total_competitors: 42,
      breakthrough_signals: 8,
      avg_threat_score: 67.5,
      active_monitoring: 38,
    })
  }),

  http.get(`${API_BASE_URL}/api/dashboard/threat-timeline`, () => {
    return HttpResponse.json([
      { date: '2025-01-01', low: 10, medium: 15, high: 5 },
      { date: '2025-01-02', low: 12, medium: 18, high: 7 },
      { date: '2025-01-03', low: 8, medium: 20, high: 10 },
      { date: '2025-01-04', low: 15, medium: 22, high: 8 },
      { date: '2025-01-05', low: 10, medium: 16, high: 6 },
      { date: '2025-01-06', low: 14, medium: 19, high: 9 },
      { date: '2025-01-07', low: 11, medium: 17, high: 5 },
    ])
  }),

  // Competitors endpoints
  http.get(`${API_BASE_URL}/api/competitors`, () => {
    return HttpResponse.json({
      items: [
        {
          id: '1',
          name: 'TechCorp Inc',
          industry: 'Technology',
          threat_score: 85,
          status: 'active',
          last_activity: '2025-01-15',
        },
        {
          id: '2',
          name: 'InnovateTech Ltd',
          industry: 'Software',
          threat_score: 72,
          status: 'active',
          last_activity: '2025-01-14',
        },
        {
          id: '3',
          name: 'DataFlow Systems',
          industry: 'Data Analytics',
          threat_score: 91,
          status: 'critical',
          last_activity: '2025-01-15',
        },
      ],
      total: 3,
      page: 1,
      page_size: 10,
    })
  }),

  http.get(`${API_BASE_URL}/api/competitors/:id/events`, () => {
    return HttpResponse.json([
      {
        id: 'evt1',
        competitor_id: '1',
        event_type: 'product_launch',
        description: 'New AI-powered platform released',
        threat_level: 'high',
        detected_at: '2025-01-15T10:30:00Z',
      },
      {
        id: 'evt2',
        competitor_id: '1',
        event_type: 'hiring',
        description: 'Hired 50 new engineers',
        threat_level: 'medium',
        detected_at: '2025-01-14T14:20:00Z',
      },
      {
        id: 'evt3',
        competitor_id: '1',
        event_type: 'partnership',
        description: 'Partnership with CloudProvider announced',
        threat_level: 'low',
        detected_at: '2025-01-13T09:15:00Z',
      },
    ])
  }),

  // Notification settings endpoints
  http.get(`${API_BASE_URL}/api/v1/users/me/notifications`, () => {
    return HttpResponse.json({
      email: { enabled: true, min_score: 70 },
      slack: { enabled: false, min_score: 80, webhook_url: '' },
      discord: { enabled: false, min_score: 75, webhook_url: '' },
      whatsapp: { enabled: false, min_score: 90, phone_number: '' },
    })
  }),

  http.patch(`${API_BASE_URL}/api/v1/users/me/notifications`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json(body)
  }),
]

export const errorHandlers = {
  unauthorized: http.get(`${API_BASE_URL}/api/auth/me`, () => {
    return HttpResponse.json(
      { detail: 'Unauthorized' },
      { status: 401 }
    )
  }),

  serverError: http.get(`${API_BASE_URL}/api/dashboard/stats`, () => {
    return HttpResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    )
  }),
}
