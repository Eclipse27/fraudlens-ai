import { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  ShieldAlert,
  LayoutDashboard,
  FileSearch,
  Building2,
  Activity,
  History,
  BrainCircuit,
  Server,
  Menu,
  Users,
  FileCheck
} from 'lucide-react';
import { cn } from '../ui';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/claim-analysis', label: 'Claim ML Analysis', icon: FileSearch },
  { path: '/provider-analysis', label: 'Provider Risk Analysis', icon: Building2 },
  { path: '/anomaly-detection', label: 'CMS Anomaly Detection', icon: Activity },
  // Phase 2 Navigation
  { path: '/patients', label: 'Patient Registry', icon: Users },
  { path: '/claim-verification', label: 'Claim Verification', icon: FileCheck },
  // System & History
  { path: '/history', label: 'Investigation History', icon: History },
  { path: '/models', label: 'Model Intelligence', icon: BrainCircuit },
  { path: '/system-status', label: 'System Status', icon: Server },
];

export const Sidebar = ({ isOpen, close }: { isOpen: boolean, close: () => void }) => {
  return (
    <>
      {/* Mobile scrim */}
      {isOpen && (
        <div className="fixed inset-0 bg-navy-900/50 z-40 md:hidden" onClick={close} />
      )}
      
      {/* Sidebar */}
      <aside className={cn(
        "fixed top-0 left-0 h-screen w-[260px] bg-navy-900 text-inverse z-50 flex flex-col transition-transform duration-250 ease-in-out md:translate-x-0 border-r border-navy-800",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-1">
            <ShieldAlert className="w-8 h-8 text-accent" />
            <span className="text-xl font-bold tracking-tight">FraudLens AI</span>
          </div>
          <p className="text-xs text-secondary font-medium uppercase tracking-wider">Insurance Intelligence</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => close()}
              className={({ isActive }) => cn(
                "flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive 
                  ? "bg-navy-800 text-accent border-l-2 border-accent" 
                  : "text-gray-400 hover:bg-navy-800 hover:text-gray-200 border-l-2 border-transparent"
              )}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-navy-800">
          <div className="flex items-center space-x-2 text-xs text-gray-500 font-medium px-2 py-2">
            <BrainCircuit className="w-4 h-4" />
            <span>AI-Powered · Phase 2 Active</span>
          </div>
        </div>
      </aside>
    </>
  );
};

export const TopBar = ({ toggleSidebar }: { toggleSidebar: () => void }) => {
  const location = useLocation();
  const title = navItems.find(i => i.path === location.pathname)?.label || 'Investigation Report';
  
  return (
    <header className="sticky top-0 z-30 flex items-center h-16 px-4 md:px-8 bg-surface/80 backdrop-blur-md border-b border-border">
      <button onClick={toggleSidebar} className="p-2 mr-4 md:hidden text-secondary hover:bg-surface-alt rounded-lg">
        <Menu className="w-6 h-6" />
      </button>
      <div className="flex items-center md:hidden mr-4">
        <ShieldAlert className="w-6 h-6 text-accent" />
      </div>
      <h1 className="text-lg font-semibold text-primary">{title}</h1>
      <div className="ml-auto flex items-center space-x-4">
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-surface-alt border border-border text-xs font-medium text-secondary">
          <span className="w-2 h-2 rounded-full bg-risk-low animate-pulse" />
          <span>Local System Connected</span>
        </div>
      </div>
    </header>
  );
};

export const PageHeader = ({ title, subtitle, action }: { title: string, subtitle?: string, action?: React.ReactNode }) => (
  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
    <div>
      <h2 className="text-3xl font-bold text-primary tracking-tight">{title}</h2>
      {subtitle && <p className="text-secondary mt-1">{subtitle}</p>}
    </div>
    {action && <div>{action}</div>}
  </div>
);

export const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} close={() => setSidebarOpen(false)} />
      <div className="md:ml-[260px] flex flex-col min-h-screen">
        <TopBar toggleSidebar={() => setSidebarOpen(true)} />
        <main className="flex-1 p-4 md:p-8 animate-in fade-in duration-200">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
