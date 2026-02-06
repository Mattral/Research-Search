import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { arxivAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import {
  Loader2, Bookmark, BookmarkCheck, ExternalLink, Calendar, Users,
  Tag, ArrowLeft, Sparkles, FileText, Copy, Share2
} from 'lucide-react';
import { toast } from 'sonner';

const ArxivPaperPage = () => {
  const { arxivId } = useParams();
  const navigate = useNavigate();
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [summarizing, setSummarizing] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        const res = await arxivAPI.getPaper(arxivId);
        setPaper(res.data);
      } catch {
        toast.error('Paper not found');
        navigate('/arxiv');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [arxivId, navigate]);

  const handleSave = async () => {
    if (!paper) return;
    try {
      if (paper.is_saved) {
        await arxivAPI.unsave(paper.arxiv_id);
        setPaper({ ...paper, is_saved: false });
        toast.success('Removed from reading list');
      } else {
        await arxivAPI.save({
          arxiv_id: paper.arxiv_id, title: paper.title, authors: paper.authors,
          summary: paper.summary, primary_category: paper.primary_category,
          published: paper.published, pdf_url: paper.pdf_url,
        });
        setPaper({ ...paper, is_saved: true });
        toast.success('Saved to reading list');
      }
    } catch { toast.error('Failed'); }
  };

  const handleSummarize = async () => {
    if (!paper) return;
    setSummarizing(true);
    try {
      const res = await arxivAPI.summarize({
        title: paper.title, abstract: paper.summary || '', authors: paper.authors,
      });
      setSummary(res.data);
    } catch {
      toast.error('Failed to generate summary');
    } finally {
      setSummarizing(false);
    }
  };

  const copyBibtex = () => {
    if (!paper) return;
    const firstAuthor = paper.authors[0]?.split(' ').pop() || 'unknown';
    const bibtex = `@article{${firstAuthor}${paper.year || ''},
  title={${paper.title}},
  author={${paper.authors.join(' and ')}},
  journal={arXiv preprint arXiv:${paper.arxiv_id}},
  year={${paper.year || ''}}
}`;
    navigator.clipboard.writeText(bibtex).then(() => toast.success('BibTeX copied')).catch(() => toast.error('Copy failed'));
  };

  const handleShare = () => {
    const url = paper?.abstract_url || window.location.href;
    navigator.clipboard.writeText(url).then(() => toast.success('Link copied')).catch(() => toast.error('Copy failed'));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background grain">
        <Header />
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (!paper) return null;

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-5xl mx-auto" data-testid="arxiv-paper-page">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="mb-6 text-muted-foreground" data-testid="back-btn">
          <ArrowLeft className="h-4 w-4 mr-1.5" /> Back
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main */}
          <div className="lg:col-span-2 space-y-5">
            <Card className="p-6 md:p-8 bg-card border-border/60" data-testid="paper-main-card">
              <div className="flex flex-wrap gap-2 mb-4">
                {paper.primary_category && <span className="cat-pill active">{paper.primary_category}</span>}
                {paper.categories?.filter(c => c !== paper.primary_category).slice(0, 4).map(c => (
                  <span key={c} className="cat-pill">{c}</span>
                ))}
              </div>

              <h1 className="font-serif text-2xl md:text-3xl font-bold mb-4 leading-tight tracking-tight">
                {paper.title}
              </h1>

              <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted-foreground mb-5">
                {paper.authors.length > 0 && (
                  <span className="flex items-center gap-1.5"><Users className="h-4 w-4" />{paper.authors.join(', ')}</span>
                )}
                {paper.published && (
                  <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4" />{paper.published.split('T')[0]}</span>
                )}
                {paper.journal_ref && (
                  <span className="flex items-center gap-1.5"><FileText className="h-4 w-4" />{paper.journal_ref}</span>
                )}
              </div>

              <div className="flex flex-wrap gap-2 mb-6">
                <Button variant={paper.is_saved ? 'default' : 'outline'} size="sm" onClick={handleSave} data-testid="save-paper-btn">
                  {paper.is_saved ? <BookmarkCheck className="h-4 w-4 mr-1.5" /> : <Bookmark className="h-4 w-4 mr-1.5" />}
                  {paper.is_saved ? 'Saved' : 'Save'}
                </Button>
                <Button variant="outline" size="sm" onClick={copyBibtex} data-testid="bibtex-btn">
                  <Copy className="h-4 w-4 mr-1.5" /> BibTeX
                </Button>
                <Button variant="outline" size="sm" onClick={handleShare} data-testid="share-paper-btn">
                  <Share2 className="h-4 w-4 mr-1.5" /> Share
                </Button>
                {paper.pdf_url && (
                  <Button variant="outline" size="sm" asChild>
                    <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4 mr-1.5" /> PDF
                    </a>
                  </Button>
                )}
                {paper.doi_url && (
                  <Button variant="outline" size="sm" asChild>
                    <a href={paper.doi_url} target="_blank" rel="noopener noreferrer">
                      <Tag className="h-4 w-4 mr-1.5" /> DOI
                    </a>
                  </Button>
                )}
              </div>

              {paper.summary && (
                <div>
                  <h2 className="font-serif text-lg font-semibold mb-2">Abstract</h2>
                  <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {paper.summary}
                  </p>
                </div>
              )}

              {paper.comment && (
                <p className="text-xs text-muted-foreground mt-4 pt-4 border-t border-border/50 italic">
                  {paper.comment}
                </p>
              )}
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-5">
            {/* AI Summary */}
            <Card className="p-5 bg-card border-border/60" data-testid="ai-summary-card">
              <h3 className="font-serif text-base font-semibold mb-3 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" /> AI Summary
              </h3>
              {!summary ? (
                <Button onClick={handleSummarize} disabled={summarizing} className="w-full" size="sm" data-testid="summarize-btn">
                  {summarizing ? (
                    <><Loader2 className="h-4 w-4 animate-spin mr-1.5" /> Analyzing...</>
                  ) : (
                    <><Sparkles className="h-4 w-4 mr-1.5" /> Generate AI Summary</>
                  )}
                </Button>
              ) : (
                <div className="space-y-3 text-sm animate-in" data-testid="ai-summary-content">
                  <p className="text-foreground leading-relaxed">{summary.summary}</p>
                  {summary.key_points.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">Key Points</h4>
                      <ul className="space-y-1">
                        {summary.key_points.map((pt, i) => (
                          <li key={i} className="text-muted-foreground text-xs leading-relaxed pl-3 relative before:content-[''] before:absolute before:left-0 before:top-2 before:w-1 before:h-1 before:rounded-full before:bg-primary">
                            {pt}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {summary.significance && (
                    <div className="p-3 bg-primary/5 rounded border border-primary/10">
                      <p className="text-xs text-primary/80 italic">{summary.significance}</p>
                    </div>
                  )}
                </div>
              )}
            </Card>

            {/* Paper Info */}
            <Card className="p-5 bg-card border-border/60">
              <h3 className="font-serif text-base font-semibold mb-3">Paper Info</h3>
              <dl className="space-y-2 text-sm">
                <div><dt className="text-xs text-muted-foreground">arXiv ID</dt><dd className="font-mono text-xs">{paper.arxiv_id}</dd></div>
                {paper.doi && <div><dt className="text-xs text-muted-foreground">DOI</dt><dd className="font-mono text-xs">{paper.doi}</dd></div>}
                {paper.updated && <div><dt className="text-xs text-muted-foreground">Last Updated</dt><dd className="text-xs">{paper.updated.split('T')[0]}</dd></div>}
              </dl>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ArxivPaperPage;
