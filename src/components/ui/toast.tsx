import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { XIcon, CircleCheckIcon } from "lucide-react"
import * as ToastPrimitives from "@radix-ui/react-toast"

import { cn } from '@/lib/utils'
import { useProgressTimer } from '@/hooks/use-progress-timer'

const ToastProvider = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Provider>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Provider>
>(({ swipeDirection = "left", ...props }, ref) => (
  <ToastPrimitives.Provider
    ref={ref}
    swipeDirection={swipeDirection}
    {...props}
  />
))
ToastProvider.displayName = ToastPrimitives.Provider.displayName

function ToastViewport({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToastPrimitives.Viewport>) {
  return (
    <ToastPrimitives.Viewport
      className={cn(
        "fixed top-4 right-4 z-50 flex max-h-screen w-full flex-col gap-2 p-0 md:max-w-[350px]",
        className
      )}
      {...props}
    />
  )
}

const toastVariants = cva(
  "group pointer-events-auto relative flex w-full items-center justify-between overflow-hidden rounded-lg border shadow-lg transition-all duration-300 data-[swipe=cancel]:translate-x-0 data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)] data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[swipe=end]:animate-out data-[state=closed]:fade-out-80 data-[state=closed]:slide-out-to-right-full data-[state=open]:slide-in-from-right-full",
  {
    variants: {
      variant: {
        default: "border bg-background text-foreground",
        destructive:
          "destructive group border-destructive bg-destructive text-white",
        success: "border-green-500 bg-green-50 text-green-900 dark:bg-green-900/20 dark:text-green-100",
        warning: "border-yellow-500 bg-yellow-50 text-yellow-900 dark:bg-yellow-900/20 dark:text-yellow-100",
        info: "border-blue-500 bg-blue-50 text-blue-900 dark:bg-blue-900/20 dark:text-blue-100",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

type ToastExtras = {
  showProgress?: boolean
  duration?: number
  progressClassName?: string
}

function Toast({
  className,
  variant,
  showProgress,
  duration = 5000,
  progressClassName,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToastPrimitives.Root> &
  VariantProps<typeof toastVariants> &
  ToastExtras) {
  const { progress, start, pause, resume } = useProgressTimer({ duration })
  const [isHovered, setIsHovered] = React.useState(false)
  const shouldAnimate = Boolean(showProgress && Number.isFinite(duration) && duration > 0)

  React.useEffect(() => {
    if (!shouldAnimate) return
    start()
  }, [shouldAnimate, start])

  React.useEffect(() => {
    if (!shouldAnimate) return
    if (isHovered) pause()
    else resume()
  }, [shouldAnimate, isHovered, pause, resume])

  return (
    <ToastPrimitives.Root
      className={cn(toastVariants({ variant }), "pb-0", className)}
      duration={duration}
      onMouseEnter={shouldAnimate ? () => setIsHovered(true) : undefined}
      onMouseLeave={shouldAnimate ? () => setIsHovered(false) : undefined}
      {...props}
    >
      <div className="flex w-full flex-col">
        <div className="flex w-full items-start gap-3 px-4 py-4">
          {props.children}
        </div>
        {shouldAnimate ? (
          <div className="px-4 pb-3">
            <div className="h-1 w-full overflow-hidden rounded-full bg-muted">
              <div
                className={cn(
                  "h-full rounded-full bg-primary transition-all duration-100 ease-linear",
                  progressClassName,
                )}
                style={{ width: `${100 - progress}%` }}
              />
            </div>
          </div>
        ) : null}
      </div>
    </ToastPrimitives.Root>
  )
}

function ToastAction({
  className,
  asChild = false,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToastPrimitives.Action>) {
  return (
    <ToastPrimitives.Action
      className={cn(
        !asChild &&
          "hover:bg-secondary focus:ring-ring group-[.destructive]:border-muted/40 hover:group-[.destructive]:border-destructive/30 hover:group-[.destructive]:bg-destructive focus:group-[.destructive]:ring-destructive focus-visible:border-ring focus-visible:ring-ring/50 inline-flex h-8 shrink-0 items-center justify-center rounded-md border bg-transparent px-3 text-sm font-medium transition-[color,box-shadow] outline-none hover:group-[.destructive]:text-white focus-visible:ring-[3px] disabled:pointer-events-none disabled:opacity-50",
        className
      )}
      asChild={asChild}
      {...props}
    >
      {props.children}
    </ToastPrimitives.Action>
  )
}

function ToastClose({
  className,
  asChild = false,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToastPrimitives.Close>) {
  return (
    <ToastPrimitives.Close
      className={cn(
        !asChild &&
          "group focus-visible:border-ring focus-visible:ring-ring/50 absolute top-3 right-3 flex size-7 items-center justify-center rounded transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:pointer-events-none",
        className
      )}
      toast-close=""
      asChild={asChild}
      {...props}
    >
      {asChild ? (
        props.children
      ) : (
        <XIcon size={16} className="opacity-60 transition-opacity group-hover:opacity-100" aria-hidden="true" />
      )}
    </ToastPrimitives.Close>
  )
}

function ToastTitle({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToastPrimitives.Title>) {
  return (
    <ToastPrimitives.Title className={cn("text-sm font-medium", className)} {...props} />
  )
}

function ToastDescription({
  className,
  ...props
}: React.ComponentPropsWithoutRef<typeof ToastPrimitives.Description>) {
  return (
    <ToastPrimitives.Description className={cn("text-muted-foreground text-sm", className)} {...props} />
  )
}

type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>
type ToastActionElement = React.ReactElement<typeof ToastAction>

interface CustomToastProps {
  title: string
  description?: string
  variant?: "default" | "destructive" | "success" | "warning" | "info"
  duration?: number
  onUndo?: () => void
  onDismiss?: () => void
}

function ToastWithProgress({ 
  title, 
  description, 
  variant = "success", 
  duration = 5000, 
  onUndo, 
  onDismiss 
}: CustomToastProps) {
  return (
    <Toast variant={variant} duration={duration} showProgress={true}>
      <div className="flex items-start gap-3">
        <CircleCheckIcon className="h-5 w-5 flex-shrink-0 text-green-600 dark:text-green-400" />
        <div className="flex-1 space-y-1">
          <ToastTitle>{title}</ToastTitle>
          {description && <ToastDescription>{description}</ToastDescription>}
        </div>
        <div className="flex items-center gap-2">
          {onUndo && (
            <ToastAction altText="Undo action" onClick={onUndo}>
              Undo
            </ToastAction>
          )}
          <ToastClose onClick={onDismiss} />
        </div>
      </div>
    </Toast>
  )
}

export {
  Toast,
  ToastAction,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
  ToastWithProgress,
  type ToastActionElement,
  type ToastProps,
  type CustomToastProps,
}
