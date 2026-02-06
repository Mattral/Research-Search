import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { paperAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { 
  Loader2, 
  Heart, 
  ExternalLink, 
  Calendar, 
  Users, 
  Building,
  ArrowLeft,
  Quote,
  Share2,
  Download
} from 'lucide-react';
import { toast } from 'sonner';

const PaperDetailPage = () => {
  const { paperId } = useParams();
  const navigate = useNavigate();
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    const fetchPaper = async () => {
      setLoading(true);
      try {
        const response = await paperAPI.getById(paperId);
        setPaper(response.data);
        
        // Track view
        await paperAPI.viewPaper(paperId);
      } catch (error) {
        toast.error('Paper not found');
        navigate('/search');
      } finally {
        setLoading(false);
      }
    };
    fetchPaper();
  }, [paperId, navigate]);

  const handleLike = async () => {
    if (!paper) return;
    
    try {
      if (paper.is_liked) {
        await paperAPI.unlikePaper(paper.paper_id);
      } else {
        await paperAPI.likePaper(paper.paper_id);
      }
      setPaper({ ...paper, is_liked: !paper.is_liked });
      toast.success(paper.is_liked ? 'Removed from favorites' : 'Added to favorites');
    } catch (error) {
      toast.error('Failed to update favorite');
    }
  };

  const handleGetRecommendations = async () => {
    setLoadingRecs(true);
    try {
      const response = await paperAPI.getRecommendations(5);
      setRecommendations(response.data);
    } catch (error) {
      toast.error('Failed to load recommendations');
    } finally {
      setLoadingRecs(false);
    }
  };

  const handleShare = async () => {
    const shareUrl = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: paper?.title,
          url: shareUrl,
        });
      } catch (error) {
        // User cancelled
      }
    } else {
      try {
        await navigator.clipboard.writeText(shareUrl);
        toast.success('Link copied to clipboard');
      } catch (error) {
        // Fallback for browsers that don't support clipboard API
        console.warn('Clipboard API not available for share');
        toast.error('Unable to copy link. Please copy manually from address bar.');
      }
    }
  };

  const handleExport = async () => {
    if (!paper) return;
    
    const citation = `${paper.authors?.join(', ')} (${paper.year}). ${paper.title}. ${paper.venue || 'Unknown venue'}.`;
    
    try {
      await navigator.clipboard.writeText(citation);
      toast.success('Citation copied to clipboard');
    } catch (error) {
      // Fallback for browsers that don't support clipboard API
      console.warn('Clipboard API not available, using fallback');
      
      // Create a temporary textarea element
      const textArea = document.createElement('textarea');
      textArea.value = citation;
      document.body.appendChild(textArea);
      textArea.select();
      
      try {
        document.execCommand('copy');
        toast.success('Citation copied to clipboard');
      } catch (fallbackError) {
        toast.error('Unable to copy citation. Please copy manually.');
        console.error('Copy fallback failed:', fallbackError);
      }
      
      document.body.removeChild(textArea);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background grain">
        <Header />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (!paper) return null;

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      
      <main className="container py-8 px-4 md:px-8 max-w-5xl mx-auto" data-testid="paper-detail-page">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="mb-6"
          data-testid="back-btn"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 animate-in">
            <Card className="p-8" data-testid="paper-detail-card">
              {/* Title */}
              <h1 className="font-serif text-3xl md:text-4xl font-bold mb-4 leading-tight">
                {paper.title}
              </h1>

              {/* Metadata */}
              <div className="flex flex-wrap gap-4 text-muted-foreground mb-6">
                {paper.authors && paper.authors.length > 0 && (
                  <span className="flex items-center gap-2">
                    <Users className="h-5 w-5" strokeWidth={1.5} />
                    {paper.authors.join(', ')}
                  </span>
                )}
                {paper.year && (
                  <span className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" strokeWidth={1.5} />
                    {paper.year}
                  </span>
                )}
                {paper.venue && (
                  <span className="flex items-center gap-2">
                    <Building className="h-5 w-5" strokeWidth={1.5} />
                    {paper.venue}
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-3 mb-8">
                <Button
                  variant={paper.is_liked ? 'default' : 'outline'}
                  onClick={handleLike}
                  data-testid="like-paper-btn"
                >
                  <Heart 
                    className="h-4 w-4 mr-2" 
                    fill={paper.is_liked ? 'currentColor' : 'none'}
                  />
                  {paper.is_liked ? 'Saved' : 'Save'}
                </Button>
                <Button variant="outline" onClick={handleShare} data-testid="share-btn">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share
                </Button>
                <Button variant="outline" onClick={handleExport} data-testid="export-btn">
                  <Download className="h-4 w-4 mr-2" />
                  Export Citation
                </Button>
                {paper.url && (
                  <Button variant="outline" asChild>
                    <a href={paper.url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      View Paper
                    </a>
                  </Button>
                )}
              </div>

              {/* Abstract */}
              {paper.abstract && (
                <div className="mb-8">
                  <h2 className="font-serif text-xl font-semibold mb-3">Abstract</h2>
                  <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {paper.abstract}
                  </p>
                </div>
              )}

              {/* Citation Count */}
              {paper.citation_count > 0 && (
                <div className="flex items-center gap-2 p-4 bg-secondary/50 rounded-lg">
                  <Quote className="h-5 w-5 text-muted-foreground" />
                  <span className="font-medium">{paper.citation_count}</span>
                  <span className="text-muted-foreground">citations</span>
                </div>
              )}
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recommend Button */}
            <Card className="p-6" data-testid="recommendations-card">
              <h3 className="font-serif text-lg font-semibold mb-4">
                Similar Papers
              </h3>
              {recommendations.length === 0 ? (
                <Button
                  onClick={handleGetRecommendations}
                  className="w-full"
                  disabled={loadingRecs}
                  data-testid="get-recommendations-btn"
                >
                  {loadingRecs ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'Recommend for me'
                  )}
                </Button>
              ) : (
                <div className="space-y-4">
                  {recommendations.map((rec) => (
                    <div
                      key={rec.paper_id}
                      className="p-3 bg-secondary/50 rounded-lg cursor-pointer hover:bg-secondary transition-colors"
                      onClick={() => navigate(`/paper/${encodeURIComponent(rec.paper_id)}`)}
                      data-testid={`rec-${rec.paper_id}`}
                    >
                      <h4 className="font-medium text-sm line-clamp-2 mb-1">
                        {rec.title}
                      </h4>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>Score: {(rec.score * 100).toFixed(0)}%</span>
                        {rec.year && <span>{rec.year}</span>}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1 italic">
                        {rec.reason}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* References */}
            {paper.references && paper.references.length > 0 && (
              <Card className="p-6">
                <h3 className="font-serif text-lg font-semibold mb-4">
                  References ({paper.references.length})
                </h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {paper.references.slice(0, 10).map((refId, index) => (
                    <div
                      key={refId}
                      className="text-sm text-muted-foreground hover:text-foreground cursor-pointer truncate"
                      onClick={() => navigate(`/paper/${encodeURIComponent(refId)}`)}
                    >
                      {index + 1}. {refId}
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Cited By */}
            {paper.cited_by && paper.cited_by.length > 0 && (
              <Card className="p-6">
                <h3 className="font-serif text-lg font-semibold mb-4">
                  Cited By ({paper.cited_by.length})
                </h3>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {paper.cited_by.slice(0, 10).map((citedId, index) => (
                    <div
                      key={citedId}
                      className="text-sm text-muted-foreground hover:text-foreground cursor-pointer truncate"
                      onClick={() => navigate(`/paper/${encodeURIComponent(citedId)}`)}
                    >
                      {index + 1}. {citedId}
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default PaperDetailPage;
