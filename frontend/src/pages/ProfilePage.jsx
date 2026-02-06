import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authAPI, paperAPI } from '../lib/api';
import Header from '../components/Header';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
  Loader2, 
  User, 
  Heart, 
  Clock, 
  Lock,
  Save,
  Eye,
  EyeOff
} from 'lucide-react';
import { toast } from 'sonner';

const ProfilePage = () => {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [favorites, setFavorites] = useState([]);
  const [recentViews, setRecentViews] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  
  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || '',
    username: user?.username || '',
  });
  
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [showPasswords, setShowPasswords] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoadingData(true);
      try {
        const [favResponse, recentResponse] = await Promise.all([
          paperAPI.getFavorites(),
          paperAPI.getRecentViews(),
        ]);
        setFavorites(favResponse.data);
        setRecentViews(recentResponse.data);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoadingData(false);
      }
    };
    fetchData();
  }, []);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await authAPI.updateProfile(profileForm);
      updateUser(response.data);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }
    
    if (passwordForm.new_password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await authAPI.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });
      toast.success('Password changed successfully');
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      
      <main className="container py-8 px-4 md:px-8" data-testid="profile-page">
        <h1 className="font-serif text-3xl md:text-4xl font-bold mb-8 flex items-center gap-3">
          <User className="h-8 w-8" strokeWidth={1.5} />
          Profile
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Profile Settings */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Information */}
            <Card data-testid="profile-info-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Profile Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleUpdateProfile} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="full_name">Full Name</Label>
                      <Input
                        id="full_name"
                        value={profileForm.full_name}
                        onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                        placeholder="Your full name"
                        data-testid="profile-fullname-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="username">Username</Label>
                      <Input
                        id="username"
                        value={profileForm.username}
                        onChange={(e) => setProfileForm({ ...profileForm, username: e.target.value })}
                        placeholder="Your username"
                        data-testid="profile-username-input"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      value={user?.email || ''}
                      disabled
                      className="bg-secondary/50"
                    />
                    <p className="text-xs text-muted-foreground">Email cannot be changed</p>
                  </div>
                  <Button type="submit" disabled={loading} data-testid="save-profile-btn">
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Save className="h-4 w-4 mr-2" />
                    )}
                    Save Changes
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Change Password */}
            <Card data-testid="change-password-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lock className="h-5 w-5" />
                  Change Password
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current_password">Current Password</Label>
                    <div className="relative">
                      <Input
                        id="current_password"
                        type={showPasswords ? 'text' : 'password'}
                        value={passwordForm.current_password}
                        onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                        placeholder="Enter current password"
                        data-testid="current-password-input"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords(!showPasswords)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showPasswords ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="new_password">New Password</Label>
                      <Input
                        id="new_password"
                        type={showPasswords ? 'text' : 'password'}
                        value={passwordForm.new_password}
                        onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                        placeholder="Min 6 characters"
                        data-testid="new-password-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirm_password">Confirm New Password</Label>
                      <Input
                        id="confirm_password"
                        type={showPasswords ? 'text' : 'password'}
                        value={passwordForm.confirm_password}
                        onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                        placeholder="Confirm password"
                        data-testid="confirm-password-input"
                      />
                    </div>
                  </div>
                  <Button type="submit" disabled={loading} data-testid="change-password-btn">
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Lock className="h-4 w-4 mr-2" />
                    )}
                    Change Password
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Activity */}
          <div className="space-y-6">
            {/* Liked Papers */}
            <Card data-testid="favorites-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-red-500" />
                  Liked Papers ({favorites.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingData ? (
                  <div className="flex justify-center py-4">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : favorites.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No liked papers yet
                  </p>
                ) : (
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {favorites.map((fav) => (
                      <div
                        key={fav.id}
                        className="p-3 bg-secondary/50 rounded-lg cursor-pointer hover:bg-secondary transition-colors"
                        onClick={() => navigate(`/paper/${encodeURIComponent(fav.paper_id)}`)}
                        data-testid={`favorite-${fav.id}`}
                      >
                        <p className="font-medium text-sm line-clamp-2">
                          {fav.paper_title || fav.paper_id}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(fav.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Views */}
            <Card data-testid="recent-views-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Recently Viewed ({recentViews.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingData ? (
                  <div className="flex justify-center py-4">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : recentViews.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No recent views
                  </p>
                ) : (
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {recentViews.map((view) => (
                      <div
                        key={view.id}
                        className="p-3 bg-secondary/50 rounded-lg cursor-pointer hover:bg-secondary transition-colors"
                        onClick={() => navigate(`/paper/${encodeURIComponent(view.paper_id)}`)}
                        data-testid={`recent-view-${view.id}`}
                      >
                        <p className="font-medium text-sm line-clamp-2">
                          {view.paper_title || view.paper_id}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(view.viewed_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Interests */}
            {user?.interests && user.interests.length > 0 && (
              <Card data-testid="interests-card">
                <CardHeader>
                  <CardTitle>Your Interests</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {user.interests.map((interest, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-secondary text-sm rounded-full"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
