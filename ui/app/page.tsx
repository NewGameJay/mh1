import { TaskList } from '@/components/task-list'
import { StatsCards } from '@/components/stats-cards'

export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <StatsCards />
      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4">Recent Tasks</h2>
        <TaskList />
      </div>
    </div>
  )
}
