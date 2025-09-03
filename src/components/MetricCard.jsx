import React from 'react'
import { formatCurrency, formatPercentage, getColorClass } from '../utils/formatters'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const MetricCard = ({ 
  title, 
  value, 
  change, 
  changeType = 'percentage',
  icon: Icon,
  trend,
  isLoading = false,
  className = ''
}) => {
  const getTrendIcon = (changeValue) => {
    if (changeValue > 0) return TrendingUp
    if (changeValue < 0) return TrendingDown
    return Minus
  }

  const TrendIcon = change !== undefined ? getTrendIcon(change) : null

  if (isLoading) {
    return (
      <div className={`bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 backdrop-blur-sm animate-pulse ${className}`}>
        <div className="flex items-center justify-between">
          <div className="space-y-3">
            <div className="h-4 bg-gray-700 rounded w-24"></div>
            <div className="h-8 bg-gray-700 rounded w-32"></div>
          </div>
          <div className="h-12 w-12 bg-gray-700 rounded-lg"></div>
        </div>
        <div className="mt-4">
          <div className="h-4 bg-gray-700 rounded w-20"></div>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-gray-800/50 rounded-xl p-6 border border-gray-700/50 backdrop-blur-sm hover:bg-gray-800/70 transition-all duration-300 hover:border-gray-600/50 hover:shadow-lg hover:shadow-blue-500/10 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">
            {typeof value === 'number' ? formatCurrency(value) : value}
          </p>
        </div>
        {Icon && (
          <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${getColorClass(change || 0)} bg-opacity-10`}>
            <Icon className={`h-6 w-6 ${getColorClass(change || 0)}`} />
          </div>
        )}
      </div>
      
      {change !== undefined && (
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {TrendIcon && (
              <TrendIcon className={`h-4 w-4 ${getColorClass(change)}`} />
            )}
            <span className={`text-sm font-semibold ${getColorClass(change)}`}>
              {changeType === 'percentage' ? formatPercentage(change) : formatCurrency(change)}
            </span>
          </div>
          {trend && (
            <span className="text-gray-400 text-xs">vs last period</span>
          )}
        </div>
      )}
    </div>
  )
}

export default MetricCard