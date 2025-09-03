import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  BarChart3, 
  PieChart, 
  FileText, 
  Home, 
  Menu, 
  X,
  TrendingUp,
  Activity,
  Settings,
  Bell,
  User
} from 'lucide-react'
import clsx from 'clsx'

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home, description: 'Market overview and insights' },
    { name: 'Trading', href: '/trading', icon: TrendingUp, description: 'Algorithmic trading strategies' },
    { name: 'Portfolio', href: '/portfolio', icon: PieChart, description: 'Portfolio optimization' },
    { name: 'Reports', href: '/reports', icon: FileText, description: 'Analysis and reports' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-blue-950">
      {/* Mobile menu */}
      <div className={clsx(
        'fixed inset-0 flex z-40 md:hidden transition-opacity duration-300',
        sidebarOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
      )}>
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        
        <div className={clsx(
          'relative flex-1 flex flex-col max-w-xs w-full bg-gray-900/95 backdrop-blur-lg border-r border-gray-700/50',
          'transform transition-transform duration-300 ease-in-out',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}>
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 text-white hover:bg-white/10 transition-colors"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          <SidebarContent navigation={navigation} currentPath={location.pathname} />
        </div>
      </div>

      {/* Static sidebar for desktop */}
      <div className="hidden md:flex md:w-72 md:flex-col md:fixed md:inset-y-0">
        <div className="flex-1 flex flex-col min-h-0 bg-gray-900/90 backdrop-blur-xl border-r border-gray-700/50">
          <SidebarContent navigation={navigation} currentPath={location.pathname} />
        </div>
      </div>

      <div className="md:pl-72 flex flex-col flex-1">
        {/* Enhanced top bar */}
        <div className="sticky top-0 z-10 bg-gray-900/80 backdrop-blur-lg border-b border-gray-700/50">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center">
              <button
                className="md:hidden -ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="h-6 w-6" />
              </button>
              <div className="ml-4 md:ml-0">
                <h1 className="text-lg font-semibold text-white">
                  {navigation.find(item => item.href === location.pathname)?.name || 'QuantFin'}
                </h1>
                <p className="text-sm text-gray-400">
                  {navigation.find(item => item.href === location.pathname)?.description || 'Quantitative Finance Platform'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
                <Bell className="h-5 w-5" />
              </button>
              <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
                <Settings className="h-5 w-5" />
              </button>
              <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        </div>
        
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

const SidebarContent = ({ navigation, currentPath }) => (
  <>
    <div className="flex items-center h-20 flex-shrink-0 px-6 bg-gradient-to-r from-blue-600 to-purple-600">
      <div className="flex items-center">
        <div className="h-10 w-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
          <Activity className="h-6 w-6 text-white" />
        </div>
        <div className="ml-3">
          <h1 className="text-xl font-bold text-white">QuantFin</h1>
          <p className="text-xs text-blue-100 opacity-90">Professional Trading</p>
        </div>
      </div>
    </div>
    
    <div className="flex-1 flex flex-col overflow-y-auto px-4 py-6">
      <nav className="flex-1 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = currentPath === item.href
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={clsx(
                'group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 transform hover:scale-105',
                isActive
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-600/25'
                  : 'text-gray-300 hover:bg-gray-800/50 hover:text-white'
              )}
            >
              <Icon className={clsx(
                'mr-3 h-5 w-5 transition-colors',
                isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'
              )} />
              <div className="flex-1">
                <div className="font-medium">{item.name}</div>
                <div className={clsx(
                  'text-xs opacity-75',
                  isActive ? 'text-blue-100' : 'text-gray-500 group-hover:text-gray-400'
                )}>
                  {item.description}
                </div>
              </div>
            </Link>
          )
        })}
      </nav>
      
      {/* Footer */}
      <div className="mt-8 pt-6 border-t border-gray-700/50">
        <div className="text-xs text-gray-500 px-4">
          <div className="flex items-center justify-between">
            <span>Version 1.0.0</span>
            <div className="flex items-center space-x-1">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Online</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </>
)

export default Layout