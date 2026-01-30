import { TaskList } from '@/components/task-list'

export default function TasksPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Tasks</h1>
        <div className="flex gap-2">
          <select className="px-3 py-2 border rounded-lg bg-white">
            <option>All Clients</option>
            <option>Acme Corp</option>
            <option>Beta Inc</option>
          </select>
          <select className="px-3 py-2 border rounded-lg bg-white">
            <option>All Status</option>
            <option>Running</option>
            <option>Completed</option>
            <option>Failed</option>
          </select>
        </div>
      </div>
      <TaskList />
    </div>
  )
}
