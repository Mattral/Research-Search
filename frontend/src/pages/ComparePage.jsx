import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { discoverAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Loader2, ArrowLeft, Sparkles, ExternalLink, GitCompare } from 'lucide-react';
import { toast } from 'sonner';

const FIELDS = ['titles', 'authors', 'years', 'citations', 'sources', 'journals', 'fields'];
const FIELD_LABELS = {
  titles: 'Title', authors: 'Authors', years: 'Year', citations: 'Citations',
  sources: 'Source', journals: 'Journal', fields: 'Fields',
};

const ComparePage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const papers = location.state?.papers || [];
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (papers.length < 2) { navigate('/discover'); return; }
    const fetch = async () => {
      try {
        const res = await discoverAPI.compare(papers);
        setComparison(res.data);
      } catch { toast.error('Comparison failed'); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background grain">
        <Header />
        <div className="flex items-center justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      </div>
    );
  }

  const matrix = comparison?.comparison_matrix;
  const aiComp = comparison?.ai_comparison;

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-6xl mx-auto" data-testid="compare-page">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="mb-4 text-muted-foreground" data-testid="compare-back-btn">
          <ArrowLeft className="h-4 w-4 mr-1" /> Back
        </Button>

        <div className="mb-6">
          <h1 className="font-serif text-2xl font-bold flex items-center gap-2">
            <GitCompare className="h-6 w-6" /> Paper Comparison
          </h1>
          <p className="text-muted-foreground text-sm">{papers.length} papers compared side-by-side</p>
        </div>

        {/* Comparison table */}
        {matrix && (
          <Card className="p-0 bg-card border-border/60 overflow-x-auto mb-6" data-testid="comparison-matrix">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border/40">
                  <th className="p-3 text-left text-xs text-muted-foreground font-medium w-28">Metric</th>
                  {matrix.titles.map((_, i) => (
                    <th key={i} className="p-3 text-left text-xs text-primary font-medium">Paper {i + 1}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {FIELDS.map(field => (
                  <tr key={field} className="border-b border-border/20 hover:bg-secondary/30 transition-colors">
                    <td className="p-3 text-xs text-muted-foreground font-medium">{FIELD_LABELS[field]}</td>
                    {matrix[field].map((val, i) => (
                      <td key={i} className="p-3 text-xs">
                        {field === 'titles' ? (
                          <span className="font-serif font-semibold text-sm leading-snug line-clamp-2">{val}</span>
                        ) : field === 'citations' ? (
                          <span className="font-mono">{val?.toLocaleString() || '0'}</span>
                        ) : (
                          <span className="text-muted-foreground">{val || 'N/A'}</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
                <tr className="border-b border-border/20">
                  <td className="p-3 text-xs text-muted-foreground font-medium">PDF</td>
                  {matrix.has_pdf.map((val, i) => (
                    <td key={i} className="p-3">
                      {val && papers[i]?.pdf_url ? (
                        <a href={papers[i].pdf_url} target="_blank" rel="noopener noreferrer"
                          className="text-primary text-xs hover:underline inline-flex items-center gap-1">
                          <ExternalLink className="h-3 w-3" /> View PDF
                        </a>
                      ) : <span className="text-xs text-muted-foreground">N/A</span>}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </Card>
        )}

        {/* AI Comparison */}
        {aiComp && (
          <Card className="p-5 bg-card border-border/60 animate-in" data-testid="ai-comparison">
            <h3 className="font-serif text-base font-semibold mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" /> AI Analysis
            </h3>
            <p className="text-sm text-foreground leading-relaxed mb-3">{aiComp.summary}</p>
            {aiComp.key_points?.length > 0 && (
              <ul className="space-y-1.5">
                {aiComp.key_points.map((pt, i) => (
                  <li key={i} className="text-xs text-muted-foreground pl-3 relative before:content-[''] before:absolute before:left-0 before:top-1.5 before:w-1 before:h-1 before:rounded-full before:bg-primary">
                    {pt}
                  </li>
                ))}
              </ul>
            )}
            {aiComp.significance && (
              <div className="mt-3 p-3 bg-primary/5 rounded border border-primary/10">
                <p className="text-xs text-primary/80 italic">{aiComp.significance}</p>
              </div>
            )}
          </Card>
        )}
      </main>
    </div>
  );
};

export default ComparePage;
