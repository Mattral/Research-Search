import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { userAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Check, Loader2, ArrowRight } from 'lucide-react';
import { toast } from 'sonner';

const OnboardingPage = () => {
  const [interests, setInterests] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const { updateUser, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // If already completed onboarding, redirect
    if (user?.has_completed_onboarding) {
      navigate('/search');
      return;
    }

    const fetchInterests = async () => {
      try {
        const response = await userAPI.getInterests();
        setInterests(response.data);
      } catch (error) {
        toast.error('Failed to load interests');
      } finally {
        setLoading(false);
      }
    };
    fetchInterests();
  }, [user, navigate]);

  const toggleInterest = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id)
        ? prev.filter((i) => i !== id)
        : [...prev, id]
    );
  };

  const handleSubmit = async () => {
    if (selectedIds.length < 3) {
      toast.error('Please select at least 3 interests');
      return;
    }

    setSubmitting(true);
    try {
      const response = await userAPI.updateInterests(selectedIds);
      updateUser(response.data);
      toast.success('Interests saved! Let\'s find papers for you.');
      navigate('/search');
    } catch (error) {
      toast.error('Failed to save interests');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-12 px-4" data-testid="onboarding-page">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-in">
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-4">
            What interests you?
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Select at least 3 topics to personalize your research feed. 
            We'll recommend papers based on your interests.
          </p>
        </div>

        {/* Interest Grid - Pinterest Style Masonry */}
        <div className="columns-2 md:columns-3 lg:columns-4 gap-4 space-y-4 mb-12" data-testid="interests-grid">
          {interests.map((interest, index) => {
            const isSelected = selectedIds.includes(interest.id);
            const heights = ['h-48', 'h-56', 'h-64', 'h-72'];
            const height = heights[index % heights.length];
            
            return (
              <div
                key={interest.id}
                onClick={() => toggleInterest(interest.id)}
                className={`
                  relative overflow-hidden rounded-2xl cursor-pointer group break-inside-avoid mb-4
                  border-2 transition-all duration-300 ${height}
                  ${isSelected 
                    ? 'border-primary ring-2 ring-primary/20' 
                    : 'border-transparent hover:border-stone-200'
                  }
                `}
                style={{
                  animationDelay: `${index * 50}ms`,
                }}
                data-testid={`interest-card-${interest.id}`}
              >
                {/* Background Image */}
                <img
                  src={interest.image_url}
                  alt={interest.name}
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                
                {/* Gradient Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                
                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute top-3 right-3 bg-primary text-primary-foreground rounded-full p-1.5 shadow-lg animate-in">
                    <Check className="h-4 w-4" strokeWidth={3} />
                  </div>
                )}
                
                {/* Label */}
                <div className="absolute bottom-0 left-0 right-0 p-4">
                  <h3 className="text-white font-semibold text-lg leading-tight">
                    {interest.name}
                  </h3>
                </div>
              </div>
            );
          })}
        </div>

        {/* Sticky Footer */}
        <div className="fixed bottom-0 left-0 right-0 p-4 glass border-t border-border/40">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              <span className="font-medium text-foreground">{selectedIds.length}</span> of 3+ selected
            </p>
            <Button
              onClick={handleSubmit}
              disabled={selectedIds.length < 3 || submitting}
              className="min-w-[140px]"
              data-testid="continue-btn"
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Continue
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;
