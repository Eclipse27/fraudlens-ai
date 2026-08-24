import { AlertCircle, Loader2 } from 'lucide-react';
import { Card, Button, cn } from '../ui';

export const LoadingState = ({ message = 'Loading...' }: { message?: string }) => (
  <div className="flex flex-col items-center justify-center p-12 text-center h-full min-h-[300px]">
    <Loader2 className="w-8 h-8 animate-spin text-accent mb-4" />
    <p className="text-secondary font-medium">{message}</p>
  </div>
);

export const ErrorState = ({ message = 'An error occurred.', onRetry }: { message?: string, onRetry?: () => void }) => (
  <div className="flex flex-col items-center justify-center p-12 text-center h-full min-h-[300px]">
    <div className="w-12 h-12 rounded-full bg-risk-high-bg flex items-center justify-center mb-4">
      <AlertCircle className="w-6 h-6 text-risk-high" />
    </div>
    <h3 className="text-lg font-semibold text-primary mb-2">Analysis Failed</h3>
    <p className="text-secondary mb-6 max-w-sm">{message}</p>
    {onRetry && <Button onClick={onRetry}>Try Again</Button>}
  </div>
);

export const EmptyState = ({ icon: Icon, title, message, action }: { icon: any, title: string, message: string, action?: React.ReactNode }) => (
  <Card className="flex flex-col items-center justify-center p-12 text-center border-dashed">
    <div className="w-12 h-12 rounded-full bg-surface-alt flex items-center justify-center mb-4">
      <Icon className="w-6 h-6 text-secondary" />
    </div>
    <h3 className="text-lg font-semibold text-primary mb-2">{title}</h3>
    <p className="text-secondary mb-6 max-w-md">{message}</p>
    {action}
  </Card>
);

export const StatusPill = ({ status }: { status: 'ONLINE' | 'OFFLINE' | 'LOADED' | 'ERROR' }) => {
  const isOk = status === 'ONLINE' || status === 'LOADED';
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border', 
      isOk ? 'bg-risk-low-bg text-risk-low border-green-200' : 'bg-risk-high-bg text-risk-high border-red-200')}>
      <span className={cn('w-1.5 h-1.5 rounded-full mr-1.5', isOk ? 'bg-risk-low' : 'bg-risk-high')} />
      {status}
    </span>
  );
};
