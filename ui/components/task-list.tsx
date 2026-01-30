'use client'

import { useState } from 'react'
import { Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react'

type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'

interface Task {
  id: string
  name: string
  skill: string
  status: TaskStatus
  startedAt: string
  completedAt?: string
  client: string
}

const statusIcons = {
  pending: Clock,
  running: Loader2,
  completed: CheckCircle,
  failed: XCircle,
}

const statusColors = {
  pending: 'text-yellow-500',
  running: 'text-blue-500',
  completed: 'text-green-500',
  failed: 'text-red-500',
}

// Mock data - replace with Firebase data
const mockTasks: Task[] = [
  {
    id: '1',
    name: 'Generate LinkedIn Posts',
    skill: 'ghostwrite-content',
    status: 'completed',
    startedAt: '2026-01-28T10:00:00Z',
    completedAt: '2026-01-28T10:15:00Z',
    client: 'Acme Corp',
  },
  {
    id: '2',
    name: 'Collect Social Signals',
    skill: 'social-listening-collect',
    status: 'running',
    startedAt: '2026-01-28T10:30:00Z',
    client: 'Acme Corp',
  },
  {
    id: '3',
    name: 'Research Competitors',
    skill: 'research-competitors',
    status: 'pending',
    startedAt: '2026-01-28T10:45:00Z',
    client: 'Beta Inc',
  },
]

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks)

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="divide-y">
        {tasks.map((task) => {
          const StatusIcon = statusIcons[task.status]
          return (
            <div key={task.id} className="p-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <StatusIcon 
                    className={`w-5 h-5 ${statusColors[task.status]} ${
                      task.status === 'running' ? 'animate-spin' : ''
                    }`} 
                  />
                  <div>
                    <p className="font-medium">{task.name}</p>
                    <p className="text-sm text-gray-500">
                      {task.skill} • {task.client}
                    </p>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  {new Date(task.startedAt).toLocaleTimeString()}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
