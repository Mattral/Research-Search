import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { arxivAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Loader2, Bookmark, BookmarkCheck, Calendar, Users, TrendingUp, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const POPULAR_CATEGORIES = [
  { code: 'cs.AI', name: 'AI' },
  { code: 'cs.LG', name: 'ML' },
  { code: 'cs.CL', name: 'NLP' },
  { code: 'cs.CV', name: 'Vision' },
  { code: 'stat.ML', name: 'Stats ML' },
  { code: 'cs.CR', name: 'Security' },
  { code: 'cs.RO', name: 'Robotics' },
  { code: 'quant-ph', name: 'Quantum' },
];

const LatestPapersPage = () => {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('cs.AI');
  const navigate = useNavigate();

  const fetchLatest = async (cat) => {
    setLoading(true);
    setActiveCategory(cat);
    try {
      const res = await arxivAPI.latest({ category: cat, max_results: 25 });
      setPapers(res.data.papers);
    } catch { toast.error('Failed to load papers'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchLatest('cs.AI'); }, []);

  const handleSave = async (paper) => {
    try {
      if (paper.is_saved) {
        await arxivAPI.unsave(paper.arxiv_id);
        setPapers(p => p.map(pp => pp.arxiv_id === paper.arxiv_id ? { ...pp, is_saved: false } : pp));
        toast.success('Removed');
      } else {
        await arxivAPI.save({
          arxiv_id: paper.arxiv_id, title: paper.title, authors: paper.authors,
          summary: paper.summary, primary_category: paper.primary_category,
          published: paper.published, pdf_url: paper.pdf_url,
        });
        setPapers(p => p.map(pp => pp.arxiv_id === paper.arxiv_id ? { ...pp, is_saved: true } : pp));
        toast.success('Saved');
      }
    } catch { toast.error('Failed'); }
  };

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-5xl mx-auto" data-testid="latest-papers-page">
        <div className="mb-6">
          <h1 className="font-serif text-3xl font-bold mb-1 flex items-center gap-2.5">
            <TrendingUp className="h-7 w-7" /> Latest Papers
          </h1>
          <p className="text-muted-foreground text-sm">Fresh research from arXiv</p>
        </div>

        {/* Category tabs */}
        <div className="flex flex-wrap gap-2 mb-6" data-testid="category-tabs">
          {POPULAR_CATEGORIES.map(cat => (
            <button key={cat.code}
              className={`cat-pill ${activeCategory === cat.code ? 'active' : ''}`}
              onClick={() => fetchLatest(cat.code)}
              data-testid={`latest-cat-${cat.code}`}>
              {cat.name}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="space-y-3">{[1,2,3,4].map(i => <div key={i} className="skeleton h-28 rounded-lg" />)}</div>
        ) : papers.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">No papers found in this category.</div>
        ) : (
          <div className="space-y-3" data-testid="latest-results">
            {papers.map((paper, idx) => (
              <Card key={paper.arxiv_id}
                className="p-5 bg-card border-border/60 hover:border-primary/30 transition-all animate-in"
                style={{ animationDelay: `${idx * 30}ms` }}
                data-testid={`latest-paper-${paper.arxiv_id}`}>
                <div className="flex gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {paper.primary_category && <span className="cat-pill">{paper.primary_category}</span>}
                      {paper.published && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />{paper.published.split('T')[0]}
                        </span>
                      )}
                    </div>
                    <h3 className="font-serif text-base font-semibold mb-1 cursor-pointer hover:text-primary transition-colors leading-snug"
                      onClick={() => navigate(`/arxiv/${encodeURIComponent(paper.arxiv_id)}`)}>
                      {paper.title}
                    </h3>
                    {paper.authors.length > 0 && (
                      <p className="text-xs text-muted-foreground truncate">
                        {paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ` +${paper.authors.length - 3}` : ''}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-col gap-1 shrink-0">
                    <Button variant="ghost" size="icon" onClick={() => handleSave(paper)}
                      className={`h-8 w-8 ${paper.is_saved ? 'text-primary' : 'text-muted-foreground'}`}
                      data-testid={`latest-save-${paper.arxiv_id}`}>
                      {paper.is_saved ? <BookmarkCheck className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
                    </Button>
                    {paper.pdf_url && (
                      <Button variant="ghost" size="icon" asChild className="h-8 w-8 text-muted-foreground">
                        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer"><ExternalLink className="h-3.5 w-3.5" /></a>
                      </Button>
                    )}
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

export default LatestPapersPage;
