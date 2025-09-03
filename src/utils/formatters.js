export const formatCurrency = (value, currency = '₹') => {
  if (value == null) return 'N/A'
  
  if (Math.abs(value) >= 1e7) {
    return `${currency}${(value / 1e7).toFixed(1)}Cr`
  }
  
  if (Math.abs(value) >= 1e5) {
    return `${currency}${(value / 1e5).toFixed(1)}L`
  }
  
  return `${currency}${value.toLocaleString()}`
}

export const formatPercentage = (value, decimals = 2) => {
  if (value == null) return 'N/A'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(decimals)}%`
}

export const formatNumber = (value, decimals = 2) => {
  if (value == null) return 'N/A'
  return value.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

export const getColorClass = (value, type = 'text') => {
  const prefix = type === 'bg' ? 'bg-' : 'text-'
  
  if (value > 0) {
    return `${prefix}green-400`
  } else if (value < 0) {
    return `${prefix}red-400`
  }
  return `${prefix}gray-400`
}

export const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

export const formatTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}