import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { recommendationAPI } from '../lib/api';
import Header from '../components/Header';
import RecommendationCard from '../components/RecommendationCard';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Loader2, Sparkles, RefreshCw, ArrowRight, Database } from 'lucide-react';
import { toast } from 'sonner';

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const [feedback, setFeedback] = useState({});
  const navigate = useNavigate();

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    try {
      const [recRes, statusRes] = await Promise.all([
        recommendationAPI.get(15),
        recommendationAPI.status().catch(() => null),
      ]);
      setRecommendations(recRes.data);
      if (statusRes) setStatus(statusRes.data);
      if (recRes.data.length === 0) {
        toast.info('Save or view a few papers (or pick interests) to get personalized picks!');
      }
    } catch (error) {
      toast.error('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchRecommendations(); }, [fetchRecommendations]);

  const handleOpen = (paperId) => navigate(`/paper/${encodeURIComponent(paperId)}`);

  const handleFeedback = async (paperId, value) => {
    const next = feedback[paperId] === value ? null : value;
    setFeedback((prev) => ({ ...prev, [paperId]: next }));
    try {
      if (next) {
        await recommendationAPI.feedback({ paper_id: paperId, feedback: next });
        toast.success(next === 'up' ? 'Thanks — we\u2019ll show more like this' : 'Got it — fewer like this');
      }
    } catch (error) {
      toast.error('Could not save feedback');
    }
  };

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-6xl mx-auto" data-testid="recommendations-page">
        <div className="flex items-start justify-between mb-8 gap-4 flex-wrap">
          <div>
            <h1 className="font-serif text-3xl md:text-4xl font-bold mb-2 flex items-center gap-3">
              <Sparkles className="h-8 w-8" strokeWidth={1.5} />
              For You
            </h1>
            <p className="text-muted-foreground">
              Hybrid picks — semantic similarity, shared authors &amp; fields, and citation impact.
            </p>
            {status && (
              <p className="text-xs text-muted-foreground/70 mt-2 inline-flex items-center gap-1.5" data-testid="rec-engine-status">
                <Database className="h-3.5 w-3.5" />
                {status.engine} engine · {status.embedding_backend} embeddings · {status.corpus_size} papers indexed
              </p>
            )}
          </div>
          <Button variant="outline" onClick={fetchRecommendations} disabled={loading} data-testid="refresh-recommendations-btn">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : recommendations.length === 0 ? (
          <Card className="p-12 text-center" data-testid="empty-recommendations">
            <Sparkles className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h2 className="font-serif text-2xl font-semibold mb-2">No recommendations yet</h2>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Pick your interests during onboarding, or save and view a few papers, and we&rsquo;ll build a personalized feed.
            </p>
            <Button onClick={() => navigate('/discover')} data-testid="explore-btn">
              Explore Papers <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="recommendations-list">
            {recommendations.map((rec) => (
              <RecommendationCard
                key={rec.paper_id}
                rec={rec}
                onOpen={handleOpen}
                onFeedback={handleFeedback}
                feedback={feedback[rec.paper_id]}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default RecommendationsPage;
