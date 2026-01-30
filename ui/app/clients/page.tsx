'use client'

import { useState } from 'react'
import { Building2, FileText, Calendar } from 'lucide-react'

interface Client {
  id: string
  name: string
  industry: string
  postsGenerated: number
  lastActivity: string
  status: 'active' | 'onboarding' | 'paused'
}

const mockClients: Client[] = [
  {
    id: 'acme',
    name: 'Acme Corp',
    industry: 'B2B SaaS',
    postsGenerated: 145,
    lastActivity: '2 hours ago',
    status: 'active',
  },
  {
    id: 'beta',
    name: 'Beta Inc',
    industry: 'Fintech',
    postsGenerated: 89,
    lastActivity: '1 day ago',
    status: 'active',
  },
  {
    id: 'gamma',
    name: 'Gamma Tech',
    industry: 'Healthcare',
    postsGenerated: 0,
    lastActivity: 'Never',
    status: 'onboarding',
  },
]

export default function ClientsPage() {
  const [clients] = useState(mockClients)

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Clients</h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Add Client
        </button>
      </div>

      <div className="grid gap-4">
        {clients.map((client) => (
          <div key={client.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-gray-500" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{client.name}</h3>
                  <p className="text-sm text-gray-500">{client.industry}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                client.status === 'active' 
                  ? 'bg-green-100 text-green-700'
                  : client.status === 'onboarding'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {client.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{client.postsGenerated} posts</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{client.lastActivity}</span>
              </div>
              <div className="flex justify-end">
                <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                  View Details →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
