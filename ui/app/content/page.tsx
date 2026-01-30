'use client'

import { useState } from 'react'
import { FileText, CheckCircle, XCircle } from 'lucide-react'

type ContentStatus = 'draft' | 'review' | 'approved' | 'rejected'

interface ContentItem {
  id: string
  title: string
  type: 'linkedin_post' | 'email' | 'report'
  status: ContentStatus
  client: string
  createdAt: string
  founder?: string
}

const statusColors = {
  draft: 'bg-gray-100 text-gray-700',
  review: 'bg-yellow-100 text-yellow-700',
  approved: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
}

// Mock data
const mockContent: ContentItem[] = [
  {
    id: '1',
    title: 'The 3 metrics that actually matter for B2B SaaS...',
    type: 'linkedin_post',
    status: 'approved',
    client: 'Acme Corp',
    createdAt: '2026-01-28',
    founder: 'Jane Doe',
  },
  {
    id: '2',
    title: 'Why we stopped measuring MQLs and started measuring...',
    type: 'linkedin_post',
    status: 'review',
    client: 'Acme Corp',
    createdAt: '2026-01-28',
    founder: 'Jane Doe',
  },
  {
    id: '3',
    title: 'Q1 Marketing Performance Report',
    type: 'report',
    status: 'draft',
    client: 'Beta Inc',
    createdAt: '2026-01-27',
  },
]

export default function ContentPage() {
  const [content, setContent] = useState(mockContent)
  const [filter, setFilter] = useState<ContentStatus | 'all'>('all')

  const filteredContent = filter === 'all' 
    ? content 
    : content.filter(c => c.status === filter)

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Content Library</h1>
        <div className="flex gap-2">
          {(['all', 'draft', 'review', 'approved', 'rejected'] as const).map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1 rounded-lg text-sm capitalize ${
                filter === status 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="divide-y">
          {filteredContent.map((item) => (
            <div key={item.id} className="p-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="font-medium">{item.title}</p>
                    <p className="text-sm text-gray-500">
                      {item.client} {item.founder && `• ${item.founder}`} • {item.createdAt}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[item.status]}`}>
                    {item.status}
                  </span>
                  {item.status === 'review' && (
                    <div className="flex gap-1">
                      <button className="p-1 text-green-600 hover:bg-green-50 rounded">
                        <CheckCircle className="w-5 h-5" />
                      </button>
                      <button className="p-1 text-red-600 hover:bg-red-50 rounded">
                        <XCircle className="w-5 h-5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
