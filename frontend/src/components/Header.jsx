import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui/button';
import {
  Search, Sparkles, User, LogOut, BookOpen, TrendingUp,
  Menu, X, FolderOpen, Database, Library
} from 'lucide-react';

const Header = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/discover', label: 'Discover', icon: Database },
    { path: '/arxiv', label: 'arXiv', icon: Search },
    { path: '/latest', label: 'Latest', icon: TrendingUp },
    { path: '/reading-list', label: 'Library', icon: Library },
    { path: '/workspaces', label: 'Projects', icon: FolderOpen },
    { path: '/recommendations', label: 'For You', icon: Sparkles },
    { path: '/profile', label: 'Profile', icon: User },
  ];

  if (!isAuthenticated) return null;

  return (
    <header className="sticky top-0 z-50 w-full glass border-b border-border/40" data-testid="header">
      <div className="container flex h-14 items-center justify-between">
        <Link to="/discover"
          className="flex items-center gap-2 font-serif text-lg font-bold hover:opacity-80 transition-opacity tracking-tight"
          data-testid="logo-link">
          <BookOpen className="h-5 w-5 text-primary" strokeWidth={1.5} />
          <span>Re<span className="text-primary">Search</span></span>
        </Link>

        <nav className="hidden md:flex items-center gap-0.5" data-testid="desktop-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link key={item.path} to={item.path}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}>
                <Icon className="h-3.5 w-3.5" strokeWidth={1.5} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{user?.full_name || user?.username}</span>
          <Button variant="ghost" size="sm" onClick={handleLogout} className="h-8 px-2 text-xs" data-testid="logout-btn">
            <LogOut className="h-3.5 w-3.5" strokeWidth={1.5} />
          </Button>
        </div>

        <Button variant="ghost" size="icon" className="md:hidden h-8 w-8"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="mobile-menu-btn">
          {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </Button>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border/40 bg-background" data-testid="mobile-menu">
          <nav className="container py-3 flex flex-col gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.path);
              return (
                <Link key={item.path} to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
                    isActive ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-secondary'
                  }`}>
                  <Icon className="h-4 w-4" strokeWidth={1.5} />
                  {item.label}
                </Link>
              );
            })}
            <hr className="my-1.5 border-border/40" />
            <button onClick={handleLogout}
              className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm text-muted-foreground hover:bg-secondary">
              <LogOut className="h-4 w-4" strokeWidth={1.5} /> Logout
            </button>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
