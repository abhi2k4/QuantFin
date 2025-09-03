import React from 'react'
import { Activity, Loader2, TrendingUp } from 'lucide-react'

const LoadingSpinner = ({ 
  message = "Loading...", 
  fullScreen = true, 
  variant = "default",
  size = "default" 
}) => {
  const sizeClasses = {
    small: "h-4 w-4",
    default: "h-8 w-8", 
    large: "h-12 w-12"
  }

  const getIcon = () => {
    switch (variant) {
      case 'trading':
        return <TrendingUp className={`${sizeClasses[size]} text-blue-400 animate-bounce`} />
      case 'pulse':
        return <Activity className={`${sizeClasses[size]} text-blue-400 animate-pulse`} />
      default:
        return <Loader2 className={`${sizeClasses[size]} text-blue-400 animate-spin`} />
    }
  }

  if (!fullScreen) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="text-center">
          {getIcon()}
          <p className="mt-2 text-gray-400 text-sm">{message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-blue-950">
      <div className="text-center">
        <div className="relative">
          {/* Outer ring */}
          <div className="h-16 w-16 border-4 border-gray-700 rounded-full animate-pulse mx-auto"></div>
          {/* Inner spinner */}
          <div className="absolute top-2 left-2">
            {getIcon()}
          </div>
        </div>
        
        <div className="mt-6 space-y-2">
          <p className="text-white font-medium">{message}</p>
          <div className="flex items-center justify-center space-x-1">
            <div className="h-1 w-2 bg-blue-400 rounded-full animate-pulse"></div>
            <div className="h-1 w-2 bg-blue-400 rounded-full animate-pulse animation-delay-100"></div>
            <div className="h-1 w-2 bg-blue-400 rounded-full animate-pulse animation-delay-200"></div>
          </div>
          <p className="text-gray-400 text-sm">Please wait while we fetch your data</p>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner