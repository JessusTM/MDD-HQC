import type { ReactNode } from 'react'

export const Layout = ({ children }: { children: ReactNode }) => (
  <div className="min-vh-100 d-flex flex-column bg-dark text-white">
    <header className="py-4 text-center border-bottom border-secondary">
      <h1 className="h3 mb-0">MDD para sistemas Híbridos Clásico-Cuańticos</h1>
    </header>
    <main className="flex-grow-1">
      <div className="container py-4">{children}</div>
    </main>
  </div>
)
