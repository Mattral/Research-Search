import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui/button';
import { 
  Search, 
  Sparkles, 
  User, 
  LogOut, 
  BookOpen,
  Menu,
  X
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
    { path: '/search', label: 'Search', icon: Search },
    { path: '/recommendations', label: 'For You', icon: Sparkles },
    { path: '/profile', label: 'Profile', icon: User },
  ];

  if (!isAuthenticated) return null;

  return (
    <header className="sticky top-0 z-50 w-full glass border-b border-border/40" data-testid="header">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <Link 
          to="/search" 
          className="flex items-center gap-2 font-serif text-xl font-bold hover:opacity-80 transition-opacity"
          data-testid="logo-link"
        >
          <BookOpen className="h-6 w-6" strokeWidth={1.5} />
          <span>Re-Search</span>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6" data-testid="desktop-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 text-sm font-medium transition-colors hover:text-primary ${
                  isActive ? 'text-primary' : 'text-muted-foreground'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className="h-4 w-4" strokeWidth={1.5} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User Info & Actions */}
        <div className="hidden md:flex items-center gap-4">
          {/* Interests Tags */}
          {user?.interests && user.interests.length > 0 && (
            <div className="flex items-center gap-2" data-testid="user-interests">
              {user.interests.slice(0, 3).map((interest, index) => (
                <span
                  key={index}
                  className="px-2 py-1 text-xs bg-secondary rounded-full text-muted-foreground"
                >
                  {interest}
                </span>
              ))}
              {user.interests.length > 3 && (
                <span className="text-xs text-muted-foreground">
                  +{user.interests.length - 3}
                </span>
              )}
            </div>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            data-testid="logout-btn"
          >
            <LogOut className="h-4 w-4 mr-2" strokeWidth={1.5} />
            Logout
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          data-testid="mobile-menu-btn"
        >
          {mobileMenuOpen ? (
            <X className="h-5 w-5" />
          ) : (
            <Menu className="h-5 w-5" />
          )}
        </Button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border/40 bg-background" data-testid="mobile-menu">
          <nav className="container py-4 flex flex-col gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                    isActive ? 'bg-secondary text-primary' : 'text-muted-foreground hover:bg-secondary'
                  }`}
                >
                  <Icon className="h-5 w-5" strokeWidth={1.5} />
                  {item.label}
                </Link>
              );
            })}
            <hr className="my-2 border-border/40" />
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-2 rounded-lg text-muted-foreground hover:bg-secondary transition-colors"
            >
              <LogOut className="h-5 w-5" strokeWidth={1.5} />
              Logout
            </button>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
