import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { paperAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  Loader2, 
  Sparkles, 
  RefreshCw,
  ArrowRight
} from 'lucide-react';
import { toast } from 'sonner';

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await paperAPI.getRecommendations(15);
      setRecommendations(response.data);
      
      if (response.data.length === 0) {
        toast.info('Start exploring papers to get personalized recommendations!');
      }
    } catch (error) {
      toast.error('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const getScoreColor = (score) => {
    if (score >= 0.7) return 'bg-success/10 text-success';
    if (score >= 0.4) return 'bg-info/10 text-info';
    return 'bg-warning/10 text-warning';
  };

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      
      <main className="container py-8 px-4 md:px-8 max-w-5xl mx-auto" data-testid="recommendations-page">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-serif text-3xl md:text-4xl font-bold mb-2 flex items-center gap-3">
              <Sparkles className="h-8 w-8" strokeWidth={1.5} />
              For You
            </h1>
            <p className="text-muted-foreground">
              Papers recommended based on your interests and activity
            </p>
          </div>
          <Button
            variant="outline"
            onClick={fetchRecommendations}
            disabled={loading}
            data-testid="refresh-recommendations-btn"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : recommendations.length === 0 ? (
          <Card className="p-12 text-center" data-testid="empty-recommendations">
            <Sparkles className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h2 className="font-serif text-2xl font-semibold mb-2">
              No recommendations yet
            </h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Start exploring and saving papers to get personalized recommendations 
              based on your research interests.
            </p>
            <Button onClick={() => navigate('/search')} data-testid="explore-btn">
              Explore Papers
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="recommendations-list">
            {recommendations.map((rec, index) => (
              <Card
                key={rec.paper_id}
                className="group p-6 hover:shadow-lg transition-all duration-300 cursor-pointer"
                onClick={() => navigate(`/paper/${encodeURIComponent(rec.paper_id)}`)}
                style={{ animationDelay: `${index * 50}ms` }}
                data-testid={`recommendation-card-${rec.paper_id}`}
              >
                {/* Score Badge */}
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mb-3 ${getScoreColor(rec.score)}`}>
                  {(rec.score * 100).toFixed(0)}% match
                </div>

                {/* Title */}
                <h3 className="font-serif text-lg font-semibold mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                  {rec.title}
                </h3>

                {/* Metadata */}
                <div className="text-sm text-muted-foreground mb-3">
                  {rec.authors && rec.authors.length > 0 && (
                    <p className="truncate">
                      {rec.authors.slice(0, 2).join(', ')}
                      {rec.authors.length > 2 && ` +${rec.authors.length - 2}`}
                    </p>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    {rec.year && <span>{rec.year}</span>}
                    {rec.venue && (
                      <>
                        <span>•</span>
                        <span className="truncate">{rec.venue}</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Reason */}
                <p className="text-xs text-muted-foreground italic border-t border-border pt-3">
                  {rec.reason}
                </p>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default RecommendationsPage;
