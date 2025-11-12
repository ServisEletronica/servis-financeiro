import React, { useState } from 'react';
import { AlertCircle, CheckCircle2, Info, AlertTriangle, Lightbulb, XCircle, Star, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export type AlertVariant = 'info' | 'warning' | 'success' | 'error' | 'tip';

interface AlertInfoProps {
  variant?: AlertVariant;
  children: React.ReactNode;
  className?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

const variantConfig = {
  info: {
    icon: Star,
    borderColor: 'border-l-[#1877f2]',
    iconColor: 'text-[#1877f2]',
  },
  warning: {
    icon: AlertTriangle,
    borderColor: 'border-l-orange-500',
    iconColor: 'text-orange-500',
  },
  success: {
    icon: CheckCircle2,
    borderColor: 'border-l-green-600',
    iconColor: 'text-green-600',
  },
  error: {
    icon: XCircle,
    borderColor: 'border-l-red-600',
    iconColor: 'text-red-600',
  },
  tip: {
    icon: Lightbulb,
    borderColor: 'border-l-[#38328B]',
    iconColor: 'text-[#38328B]',
  },
};

export const AlertInfo: React.FC<AlertInfoProps> = ({
  variant = 'info',
  children,
  className,
  dismissible = false,
  onDismiss,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const config = variantConfig[variant];
  const Icon = config.icon;

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss?.();
  };

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        'relative flex gap-3 p-3 rounded border-l-[4px] bg-white dark:bg-gray-900',
        config.borderColor,
        className
      )}
      style={{
        boxShadow: 'rgba(0, 0, 0, 0.1) 0px 0px 5px 0px, rgba(0, 0, 0, 0.1) 0px 0px 1px 0px'
      }}
    >
      <div className="flex-shrink-0 mt-0.5">
        <Icon className={cn('h-4 w-4', config.iconColor)} />
      </div>
      <div className="flex-1 text-sm text-foreground leading-relaxed">{children}</div>
      {dismissible && (
        <button
          type="button"
          onClick={handleDismiss}
          className="flex-shrink-0 -mt-1 -mr-1 p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          aria-label="Fechar"
        >
          <X className="h-4 w-4 text-muted-foreground" />
        </button>
      )}
    </div>
  );
};
