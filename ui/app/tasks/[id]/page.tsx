'use client'

import { useParams } from 'next/navigation'
import { ArrowLeft, Clock, CheckCircle } from 'lucide-react'
import Link from 'next/link'

export default function TaskDetailPage() {
  const params = useParams()
  const taskId = params.id

  // Mock task data - replace with Firebase
  const task = {
    id: taskId,
    name: 'Generate LinkedIn Posts',
    skill: 'ghostwrite-content',
    status: 'completed',
    startedAt: '2026-01-28T10:00:00Z',
    completedAt: '2026-01-28T10:15:00Z',
    client: 'Acme Corp',
    logs: [
      { time: '10:00:00', message: 'Starting ghostwrite-content skill' },
      { time: '10:02:00', message: 'Loading client context from Firebase' },
      { time: '10:05:00', message: 'Fetching social signals (45 found)' },
      { time: '10:08:00', message: 'Generating posts with claude-sonnet-4' },
      { time: '10:12:00', message: 'QA review passed (score: 0.92)' },
      { time: '10:15:00', message: 'Completed: 5 posts generated' },
    ],
    output: {
      postsGenerated: 5,
      tokensUsed: 12500,
      cost: '$0.45',
    }
  }

  return (
    <div className="p-6">
      <Link href="/tasks" className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-4">
        <ArrowLeft className="w-4 h-4" />
        Back to Tasks
      </Link>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">{task.name}</h1>
            <p className="text-gray-500">{task.skill} • {task.client}</p>
          </div>
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="w-5 h-5" />
            <span className="font-medium">Completed</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-500">Posts Generated</p>
            <p className="text-2xl font-bold">{task.output.postsGenerated}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-500">Tokens Used</p>
            <p className="text-2xl font-bold">{task.output.tokensUsed.toLocaleString()}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-500">Cost</p>
            <p className="text-2xl font-bold">{task.output.cost}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Execution Log</h2>
        <div className="font-mono text-sm bg-gray-900 text-gray-100 rounded-lg p-4 max-h-96 overflow-auto">
          {task.logs.map((log, i) => (
            <div key={i} className="py-1">
              <span className="text-gray-500">[{log.time}]</span>{' '}
              <span>{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
