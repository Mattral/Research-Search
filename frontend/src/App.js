import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import OnboardingPage from './pages/OnboardingPage';
import SearchPage from './pages/SearchPage';
import PaperDetailPage from './pages/PaperDetailPage';
import RecommendationsPage from './pages/RecommendationsPage';
import ProfilePage from './pages/ProfilePage';
import ArxivSearchPage from './pages/ArxivSearchPage';
import ArxivPaperPage from './pages/ArxivPaperPage';
import ReadingListPage from './pages/ReadingListPage';
import LatestPapersPage from './pages/LatestPapersPage';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  );
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
};

const OnboardingGuard = ({ children }) => {
  const { user } = useAuth();
  if (user && !user.has_completed_onboarding) return <Navigate to="/onboarding" replace />;
  return children;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  );
  if (isAuthenticated) {
    if (!user?.has_completed_onboarding) return <Navigate to="/onboarding" replace />;
    return <Navigate to="/arxiv" replace />;
  }
  return children;
};

const Guarded = ({ children }) => (
  <ProtectedRoute><OnboardingGuard>{children}</OnboardingGuard></ProtectedRoute>
);

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/onboarding" element={<ProtectedRoute><OnboardingPage /></ProtectedRoute>} />
      <Route path="/arxiv" element={<Guarded><ArxivSearchPage /></Guarded>} />
      <Route path="/arxiv/:arxivId" element={<Guarded><ArxivPaperPage /></Guarded>} />
      <Route path="/latest" element={<Guarded><LatestPapersPage /></Guarded>} />
      <Route path="/reading-list" element={<Guarded><ReadingListPage /></Guarded>} />
      <Route path="/search" element={<Guarded><SearchPage /></Guarded>} />
      <Route path="/paper/:paperId" element={<Guarded><PaperDetailPage /></Guarded>} />
      <Route path="/recommendations" element={<Guarded><RecommendationsPage /></Guarded>} />
      <Route path="/profile" element={<Guarded><ProfilePage /></Guarded>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster
          position="top-right"
          theme="dark"
          richColors
          closeButton
          toastOptions={{ duration: 3000 }}
        />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
