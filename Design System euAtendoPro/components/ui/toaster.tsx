import { useToast } from '@/hooks/use-toast'
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from '@/components/ui/toast'
import {
  AlertTriangle,
  CheckCircle2,
  Info,
  XCircle,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const BASE_CONTAINER =
  'relative flex w-full overflow-hidden rounded-lg bg-white text-foreground shadow-lg before:absolute before:inset-y-0 before:left-0 before:w-[6px] before:content-["" ]'

const TOAST_THEME = {
  default: {
    icon: Info,
    container: cn(BASE_CONTAINER, 'border border-primary/25 bg-primary/5 before:bg-primary/70'),
    iconBg: 'bg-white text-primary shadow-sm',
    progress: 'bg-primary',
  },
  success: {
    icon: CheckCircle2,
    container: cn(
      BASE_CONTAINER,
      'border border-emerald-500/40 bg-emerald-50 text-emerald-900 before:bg-emerald-500',
    ),
    iconBg: 'bg-white text-emerald-600 shadow-sm',
    progress: 'bg-emerald-500',
  },
  destructive: {
    icon: XCircle,
    container: cn(
      BASE_CONTAINER,
      'border border-rose-500/40 bg-rose-50 text-rose-900 before:bg-rose-500',
    ),
    iconBg: 'bg-white text-rose-600 shadow-sm',
    progress: 'bg-rose-500',
  },
  warning: {
    icon: AlertTriangle,
    container: cn(
      BASE_CONTAINER,
      'border border-amber-500/40 bg-amber-50 text-amber-900 before:bg-amber-500',
    ),
    iconBg: 'bg-white text-amber-600 shadow-sm',
    progress: 'bg-amber-500',
  },
  info: {
    icon: Info,
    container: cn(
      BASE_CONTAINER,
      'border border-sky-500/40 bg-sky-50 text-sky-900 before:bg-sky-500',
    ),
    iconBg: 'bg-white text-sky-600 shadow-sm',
    progress: 'bg-sky-500',
  },
} as const

type ToastVariant = keyof typeof TOAST_THEME

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <ToastProvider>
      {toasts.map(({ id, title, description, action, variant = 'default', showProgress, duration, ...props }) => {
        const theme = TOAST_THEME[(variant as ToastVariant) ?? 'default'] ?? TOAST_THEME.default
        const Icon = theme.icon
        const progressEnabled = showProgress ?? true
        const computedDuration = duration ?? 5000

        return (
          <Toast
            key={id}
            variant="default"
            className={cn(theme.container)}
            showProgress={progressEnabled}
            progressClassName={theme.progress}
            duration={computedDuration}
            {...props}
            onOpenChange={(open) => {
              props.onOpenChange?.(open)
              if (!open) dismiss(id)
            }}
          >
            <div className="flex w-full items-start gap-3 pl-5 pr-4">
              <span
                className={cn(
                  'mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full',
                  theme.iconBg,
                )}
              >
                <Icon className="h-5 w-5" aria-hidden="true" />
              </span>
              <div className="flex-1">
                {title ? <ToastTitle className="text-sm font-semibold leading-tight">{title}</ToastTitle> : null}
                {description ? (
                  <ToastDescription className="mt-1 text-sm text-foreground/80">
                    {description}
                  </ToastDescription>
                ) : null}
              </div>
              {action ? <div className="flex-shrink-0">{action}</div> : null}
              <ToastClose className="ml-2 text-foreground/50 transition hover:text-foreground" />
            </div>
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
