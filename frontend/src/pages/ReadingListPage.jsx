import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { arxivAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Loader2, BookOpen, Trash2, ExternalLink, Calendar, Users } from 'lucide-react';
import { toast } from 'sonner';

const ReadingListPage = () => {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await arxivAPI.readingList();
        setPapers(res.data);
      } catch { toast.error('Failed to load reading list'); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const handleRemove = async (arxivId) => {
    try {
      await arxivAPI.unsave(arxivId);
      setPapers(p => p.filter(pp => pp.arxiv_id !== arxivId));
      toast.success('Removed from reading list');
    } catch { toast.error('Failed to remove'); }
  };

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-4xl mx-auto" data-testid="reading-list-page">
        <div className="mb-8">
          <h1 className="font-serif text-3xl font-bold mb-1 flex items-center gap-2.5">
            <BookOpen className="h-7 w-7" /> Reading List
          </h1>
          <p className="text-muted-foreground text-sm">{papers.length} saved papers</p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
        ) : papers.length === 0 ? (
          <Card className="p-12 text-center bg-card border-border/60" data-testid="empty-reading-list">
            <BookOpen className="h-10 w-10 mx-auto mb-3 text-muted-foreground opacity-40" />
            <h2 className="font-serif text-xl font-semibold mb-2">No saved papers</h2>
            <p className="text-muted-foreground text-sm mb-5">Search arXiv and save papers to build your reading list.</p>
            <Button onClick={() => navigate('/arxiv')} data-testid="go-search-btn">Browse arXiv</Button>
          </Card>
        ) : (
          <div className="space-y-3" data-testid="reading-list">
            {papers.map((paper, idx) => (
              <Card key={paper.arxiv_id}
                className="p-5 bg-card border-border/60 hover:border-primary/30 transition-all animate-in"
                style={{ animationDelay: `${idx * 40}ms` }}
                data-testid={`reading-item-${paper.arxiv_id}`}>
                <div className="flex gap-4">
                  <div className="flex-1 min-w-0">
                    {paper.primary_category && <span className="cat-pill mb-1.5 inline-block">{paper.primary_category}</span>}
                    <h3 className="font-serif text-lg font-semibold mb-1 cursor-pointer hover:text-primary transition-colors"
                      onClick={() => navigate(`/arxiv/${encodeURIComponent(paper.arxiv_id)}`)}>
                      {paper.title}
                    </h3>
                    <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                      {paper.authors_str && (
                        <span className="flex items-center gap-1"><Users className="h-3 w-3" />{paper.authors_str.split(',').slice(0,3).join(', ')}</span>
                      )}
                      {paper.published && (
                        <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{paper.published.split('T')[0]}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col gap-1.5 shrink-0">
                    {paper.pdf_url && (
                      <Button variant="ghost" size="icon" asChild className="text-muted-foreground h-8 w-8">
                        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer"><ExternalLink className="h-4 w-4" /></a>
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" onClick={() => handleRemove(paper.arxiv_id)}
                      className="text-muted-foreground hover:text-destructive h-8 w-8" data-testid={`remove-btn-${paper.arxiv_id}`}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default ReadingListPage;
