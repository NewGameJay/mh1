'use client'

import { FileText, Zap, Clock, DollarSign } from 'lucide-react'

const stats = [
  { name: 'Tasks Today', value: '12', icon: Zap, change: '+3' },
  { name: 'Content Generated', value: '45', icon: FileText, change: '+8' },
  { name: 'Avg. Runtime', value: '4.2m', icon: Clock, change: '-0.5m' },
  { name: 'Cost Today', value: '$12.50', icon: DollarSign, change: '' },
]

export function StatsCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.name} className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">{stat.name}</p>
              <p className="text-2xl font-bold mt-1">{stat.value}</p>
              {stat.change && (
                <p className="text-sm text-green-500 mt-1">{stat.change}</p>
              )}
            </div>
            <stat.icon className="w-8 h-8 text-gray-400" />
          </div>
        </div>
      ))}
    </div>
  )
}
