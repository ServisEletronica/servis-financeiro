import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Menu } from 'lucide-react'
import { Link } from 'react-router-dom'

export function MobileNav() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="shrink-0 md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="flex flex-col">
        <nav className="grid gap-2 text-lg font-medium">
          <Link
            to="/panel"
            className="flex items-center gap-2 text-lg font-semibold"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                className="h-7 w-7"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M7.9 20A9 9 0 1 0 4 16.1L2 22z"
                  className="fill-card stroke-card"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M8 12h.01M12 12h.01M16 12h.01"
                  className="stroke-primary"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <span className="text-lg tracking-tight text-foreground">
              Template<span className="font-bold">App</span>
            </span>
          </Link>
          <Link
            to="/panel"
            className="mx-[-0.65rem] flex items-center gap-4 rounded-xl px-3 py-2 text-muted-foreground hover:text-foreground"
          >
            Dashboard
          </Link>
        </nav>
      </SheetContent>
    </Sheet>
  )
}
