import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { AlertCircle, AlertTriangle, CheckCircle, Search } from 'lucide-react';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Button Component
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  isLoading?: boolean;
}
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', isLoading, children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none active:scale-95';
    const variants = {
      primary: 'bg-accent text-white hover:bg-accent-hover focus:ring-accent',
      secondary: 'bg-surface-alt text-primary hover:bg-gray-200 focus:ring-gray-400',
      outline: 'border border-border text-primary hover:bg-surface-alt focus:ring-gray-400',
      danger: 'bg-risk-high text-white hover:bg-red-700 focus:ring-risk-high',
    };
    return (
      <button ref={ref} className={cn(baseStyles, variants[variant], className)} disabled={isLoading || props.disabled} {...props}>
        {isLoading && <span className="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />}
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';

// Card Component
export const Card = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn('bg-surface rounded-lg shadow-sm border border-border overflow-hidden', className)} {...props}>
    {children}
  </div>
);

// RiskBadge Component
export const RiskBadge = ({ level, className }: { level: string, className?: string }) => {
  const normalized = level.toUpperCase();
  const configs: Record<string, { bg: string, text: string, icon: any }> = {
    LOW: { bg: 'bg-risk-low-bg', text: 'text-risk-low', icon: CheckCircle },
    MEDIUM: { bg: 'bg-risk-medium-bg', text: 'text-risk-medium', icon: AlertTriangle },
    HIGH: { bg: 'bg-risk-high-bg', text: 'text-risk-high', icon: AlertCircle },
    SUSPICIOUS: { bg: 'bg-risk-suspicious-bg', text: 'text-risk-suspicious', icon: Search },
    'SUSPICIOUS PATTERN': { bg: 'bg-risk-suspicious-bg', text: 'text-risk-suspicious', icon: Search },
    'NORMAL PATTERN': { bg: 'bg-risk-low-bg', text: 'text-risk-low', icon: CheckCircle }
  };
  const config = configs[normalized] || configs['LOW'];
  const Icon = config.icon;
  return (
    <span className={cn(`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text}`, className)}>
      <Icon className="w-3.5 h-3.5 mr-1" />
      {level.toUpperCase()}
    </span>
  );
};

// Input Component
export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement> & { label: string, error?: string }>(
  ({ className, label, error, ...props }, ref) => (
    <div className="flex flex-col space-y-1.5">
      <label className="text-sm font-medium text-secondary">{label}</label>
      <input ref={ref} className={cn('flex h-10 w-full rounded-lg border border-border bg-transparent px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-accent', error && 'border-risk-high focus:ring-risk-high', className)} {...props} />
      {error && <span className="text-xs text-risk-high">{error}</span>}
    </div>
  )
);
Input.displayName = 'Input';

// Select Component
export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement> & { label: string, options: string[], error?: string }>(
  ({ className, label, options, error, ...props }, ref) => (
    <div className="flex flex-col space-y-1.5">
      <label className="text-sm font-medium text-secondary">{label}</label>
      <select ref={ref} className={cn('flex h-10 w-full rounded-lg border border-border bg-transparent px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent', error && 'border-risk-high focus:ring-risk-high', className)} {...props}>
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
      {error && <span className="text-xs text-risk-high">{error}</span>}
    </div>
  )
);
Select.displayName = 'Select';

// RiskScoreGauge Component
export const RiskScoreGauge = ({ score }: { score: number }) => {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;
  
  let colorClass = 'text-risk-low';
  if (score > 30) colorClass = 'text-risk-medium';
  if (score > 60) colorClass = 'text-risk-high';

  return (
    <div className="relative flex items-center justify-center w-32 h-32" aria-label={`Risk score ${score} out of 100`}>
      <svg className="transform -rotate-90 w-32 h-32">
        <circle cx="64" cy="64" r={radius} className="stroke-surface-alt" strokeWidth="8" fill="transparent" />
        <circle 
          cx="64" cy="64" r={radius} 
          className={cn("transition-all duration-700 ease-out", colorClass)} 
          strokeWidth="8" fill="transparent" 
          strokeDasharray={circumference} 
          strokeDashoffset={strokeDashoffset} 
          strokeLinecap="round" 
          stroke="currentColor"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-3xl font-bold tabular-nums text-primary">{Math.round(score)}</span>
        <span className="text-xs text-secondary font-medium">/ 100</span>
      </div>
    </div>
  );
};
