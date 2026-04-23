import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { IconLayoutDashboard, IconBrain, IconChartBar, IconChartLine, IconSettings, IconHome, IconChevronRight } from '@tabler/icons-react';

interface NavButton {
  path: string;
  label: string;
  icon: React.ElementType;
  gradient: string;
  description?: string;
}

const navigationButtons: NavButton[] = [
  {
    path: '/dashboard',
    label: 'Dashboard',
    icon: IconLayoutDashboard,
    gradient: 'from-blue-500 to-cyan-500',
    description: 'Portfolio Overview'
  },
  {
    path: '/analytics',
    label: 'ML Analytics',
    icon: IconChartLine,
    gradient: 'from-purple-500 to-pink-500',
    description: 'Model Comparison & Charts'
  },
  {
    path: '/models',
    label: 'Model Insights',
    icon: IconBrain,
    gradient: 'from-green-500 to-emerald-500',
    description: 'AI Performance'
  },
  {
    path: '/backtest',
    label: 'Backtesting',
    icon: IconChartBar,
    gradient: 'from-orange-500 to-red-500',
    description: 'Strategy Testing'
  }
];

export default function PageNavigation() {
  const navigate = useNavigate();
  const location = useLocation();

  const currentButtons = navigationButtons.filter(btn => btn.path !== location.pathname);

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <div className="flex flex-col gap-3">
        {/* IconHome Button */}
        {location.pathname !== '/' && (
          <Button
            onClick={() => navigate('/')}
            className="bg-gray-800/90 hover:bg-gray-700 text-white shadow-xl backdrop-blur-sm border border-gray-700 h-12 px-4 rounded-xl group"
            title="Go to IconHome"
          >
            <IconHome className="w-5 h-5 mr-2" />
            <span className="font-medium">IconHome</span>
          </Button>
        )}

        {/* Navigation Buttons - Show all except current page */}
        {currentButtons.map((btn) => (
          <Button
            key={btn.path}
            onClick={() => navigate(btn.path)}
            className={`bg-gradient-to-r ${btn.gradient} hover:opacity-90 text-white shadow-xl backdrop-blur-sm h-12 px-4 rounded-xl group transition-all hover:scale-105`}
            title={btn.description}
          >
            <btn.icon className="w-5 h-5 mr-2" />
            <span className="font-medium">{btn.label}</span>
            <IconChevronRight className="w-4 h-4 ml-1 opacity-70 group-hover:translate-x-1 transition-transform" />
          </Button>
        ))}

        {/* IconSettings Button */}
        {location.pathname !== '/settings' && (
          <Button
            onClick={() => navigate('/settings')}
            className="bg-gray-800/90 hover:bg-gray-700 text-white shadow-xl backdrop-blur-sm border border-gray-700 h-12 px-4 rounded-xl group"
            title="IconSettings"
          >
            <IconSettings className="w-5 h-5 mr-2" />
            <span className="font-medium">IconSettings</span>
          </Button>
        )}
      </div>
    </div>
  );
}
