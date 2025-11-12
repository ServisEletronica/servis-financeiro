import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { Toaster as Sonner } from '@/components/ui/sonner'
import { TooltipProvider } from '@/components/ui/tooltip'
import { ThemeProvider } from '@/components/ThemeProvider'
import { CustomToastProvider } from '@/components/CustomToastProvider'

import Layout from './components/Layout'
import LoginPage from './pages/Login'
import ProjetadoPage from './pages/Projetado'
import SettingsPage from './pages/Settings'
import NotFound from './pages/NotFound'
import { AuthProvider } from './context/auth-context'
import { ProtectedRoute } from './components/ProtectedRoute'
import { SidebarProvider } from './context/sidebar-context'

const App = () => (
  <BrowserRouter>
    <ThemeProvider defaultTheme="system" storageKey="app-theme">
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <CustomToastProvider>
          <AuthProvider>
            <SidebarProvider>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/"
                  element={<Navigate to="/projetado" replace />}
                />
                <Route
                  element={(
                    <ProtectedRoute>
                      <Layout />
                    </ProtectedRoute>
                  )}
                >
                  <Route path="/projetado" element={<ProjetadoPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Route>
                <Route path="*" element={<NotFound />} />
              </Routes>
            </SidebarProvider>
          </AuthProvider>
        </CustomToastProvider>
      </TooltipProvider>
    </ThemeProvider>
  </BrowserRouter>
)

export default App
