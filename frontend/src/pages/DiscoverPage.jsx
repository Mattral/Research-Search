import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { discoverAPI, arxivAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Search, Loader2, Bookmark, BookmarkCheck, ExternalLink,
  Calendar, Users, TrendingUp, GitCompare, ChevronDown, ChevronUp,
  Database, BarChart2
} from 'lucide-react';
import { toast } from 'sonner';

const SOURCE_LABELS = {
  arxiv: { label: 'arXiv', color: 'text-red-400' },
  semantic_scholar: { label: 'S2', color: 'text-blue-400' },
  openalex: { label: 'OA', color: 'text-green-400' },
};

const DiscoverPage = () => {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [sources, setSources] = useState('arxiv,semantic_scholar,openalex');
  const [totalResults, setTotalResults] = useState(0);
  const [sourcesSearched, setSourcesSearched] = useState([]);
  const [sort, setSort] = useState('relevance');
  const [compareList, setCompareList] = useState([]);
  const [trendData, setTrendData] = useState(null);
  const [trendLoading, setTrendLoading] = useState(false);
  const [showTrends, setShowTrends] = useState(false);
  const navigate = useNavigate();

  const handleSearch = useCallback(async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await discoverAPI.search({ query, sources, limit: 15, sort });
      setPapers(res.data.papers);
      setTotalResults(res.data.total_results);
      setSourcesSearched(res.data.sources_searched);
    } catch { toast.error('Search failed'); }
    finally { setLoading(false); }
  }, [query, sources, sort]);

  const fetchTrends = async () => {
    if (!query.trim()) { toast.error('Enter a search query first'); return; }
    setTrendLoading(true);
    setShowTrends(true);
    try {
      const res = await discoverAPI.trends({ query });
      setTrendData(res.data.trend_data);
    } catch { toast.error('Failed to load trends'); }
    finally { setTrendLoading(false); }
  };

  const toggleCompare = (paper) => {
    setCompareList(prev => {
      const exists = prev.find(p => p.source_id === paper.source_id && p.source === paper.source);
      if (exists) return prev.filter(p => !(p.source_id === paper.source_id && p.source === paper.source));
      if (prev.length >= 5) { toast.error('Max 5 papers for comparison'); return prev; }
      return [...prev, paper];
    });
  };

  const isInCompare = (paper) => compareList.some(p => p.source_id === paper.source_id && p.source === paper.source);

  const maxTrend = trendData ? Math.max(...trendData.map(t => t.count), 1) : 1;

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-5xl mx-auto" data-testid="discover-page">
        <div className="mb-6">
          <h1 className="font-serif text-3xl md:text-4xl font-bold mb-1 tracking-tight flex items-center gap-2.5">
            <Database className="h-7 w-7" /> Discover
          </h1>
          <p className="text-muted-foreground text-sm">
            Search across arXiv, Semantic Scholar & OpenAlex simultaneously
          </p>
        </div>

        {/* Search bar */}
        <form onSubmit={handleSearch} className="mb-5 space-y-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input value={query} onChange={e => setQuery(e.target.value)}
                placeholder="Search across multiple databases..."
                className="pl-10 h-11 bg-secondary border-border" data-testid="discover-search-input" />
            </div>
            <Button type="submit" className="h-11 px-6" disabled={loading} data-testid="discover-search-btn">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
            </Button>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Source toggles */}
            <div className="flex gap-1.5">
              {Object.entries(SOURCE_LABELS).map(([key, { label }]) => {
                const active = sources.includes(key);
                return (
                  <button key={key} type="button"
                    className={`cat-pill ${active ? 'active' : ''}`}
                    onClick={() => {
                      const list = sources.split(',').filter(Boolean);
                      setSources(active ? list.filter(s => s !== key).join(',') : [...list, key].join(','));
                    }}
                    data-testid={`source-${key}`}>
                    {label}
                  </button>
                );
              })}
            </div>
            <select value={sort} onChange={e => setSort(e.target.value)}
              className="h-8 px-3 rounded-md bg-secondary border border-border text-xs text-foreground" data-testid="discover-sort">
              <option value="relevance">Relevance</option>
              <option value="citations">Citations</option>
              <option value="year">Newest</option>
            </select>
            <Button type="button" variant="outline" size="sm" onClick={fetchTrends} disabled={trendLoading}
              className="h-8 text-xs" data-testid="trends-btn">
              <BarChart2 className="h-3.5 w-3.5 mr-1" /> Trends
            </Button>
          </div>
        </form>

        {/* Trend chart */}
        {showTrends && (
          <Card className="p-5 bg-card border-border/60 mb-5 animate-in" data-testid="trend-chart">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-serif text-sm font-semibold flex items-center gap-1.5">
                <TrendingUp className="h-4 w-4 text-primary" /> Publication Trend: "{query}"
              </h3>
              <Button variant="ghost" size="sm" onClick={() => setShowTrends(false)} className="h-6 w-6 p-0">
                <ChevronUp className="h-4 w-4" />
              </Button>
            </div>
            {trendLoading ? (
              <div className="flex justify-center py-6"><Loader2 className="h-5 w-5 animate-spin text-muted-foreground" /></div>
            ) : trendData ? (
              <div className="flex items-end gap-1.5 h-32">
                {trendData.map((d, i) => (
                  <div key={d.year} className="flex-1 flex flex-col items-center gap-1 group" data-testid={`trend-bar-${d.year}`}>
                    <span className="text-[10px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                      {d.count.toLocaleString()}
                    </span>
                    <div
                      className="w-full bg-primary/70 rounded-t transition-all hover:bg-primary"
                      style={{ height: `${Math.max((d.count / maxTrend) * 100, 2)}%`, minHeight: '2px' }}
                    />
                    <span className="text-[10px] text-muted-foreground">{String(d.year).slice(2)}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </Card>
        )}

        {/* Compare bar */}
        {compareList.length > 0 && (
          <div className="flex items-center gap-3 p-3 mb-4 bg-secondary/80 rounded-lg border border-primary/20 animate-in" data-testid="compare-bar">
            <GitCompare className="h-4 w-4 text-primary shrink-0" />
            <span className="text-xs text-muted-foreground">{compareList.length} selected</span>
            <div className="flex-1 flex gap-1 overflow-x-auto">
              {compareList.map(p => (
                <span key={`${p.source}-${p.source_id}`}
                  className="cat-pill active text-[10px] cursor-pointer"
                  onClick={() => toggleCompare(p)}>
                  {p.title.slice(0, 25)}...
                </span>
              ))}
            </div>
            <Button size="sm" className="h-7 text-xs"
              onClick={() => navigate('/compare', { state: { papers: compareList } })}
              disabled={compareList.length < 2} data-testid="compare-go-btn">
              Compare
            </Button>
          </div>
        )}

        {/* Results info */}
        {sourcesSearched.length > 0 && (
          <div className="flex items-center gap-2 mb-3 text-xs text-muted-foreground">
            <span>{totalResults.toLocaleString()} results from</span>
            {sourcesSearched.map(s => (
              <span key={s} className={`font-medium ${SOURCE_LABELS[s]?.color || ''}`}>
                {SOURCE_LABELS[s]?.label || s}
              </span>
            ))}
          </div>
        )}

        {/* Results */}
        {loading ? (
          <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-28 rounded-lg" />)}</div>
        ) : papers.length === 0 && query ? (
          <div className="text-center py-16 text-muted-foreground">
            <Search className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p>No papers found. Try a broader query.</p>
          </div>
        ) : papers.length === 0 ? (
          <div className="text-center py-16 text-muted-foreground">
            <Database className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Search across arXiv, Semantic Scholar, and OpenAlex</p>
          </div>
        ) : (
          <div className="space-y-3" data-testid="discover-results">
            {papers.map((paper, idx) => (
              <Card key={`${paper.source}-${paper.source_id}`}
                className="p-4 bg-card border-border/60 hover:border-primary/30 transition-all animate-in"
                style={{ animationDelay: `${idx * 30}ms` }}
                data-testid={`discover-paper-${paper.source_id}`}>
                <div className="flex gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-[10px] font-bold uppercase tracking-wider ${SOURCE_LABELS[paper.source]?.color || 'text-muted-foreground'}`}>
                        {SOURCE_LABELS[paper.source]?.label || paper.source}
                      </span>
                      {paper.year && <span className="text-xs text-muted-foreground flex items-center gap-0.5"><Calendar className="h-3 w-3" />{paper.year}</span>}
                      {paper.citation_count > 0 && <span className="text-xs text-muted-foreground">{paper.citation_count} citations</span>}
                    </div>
                    <h3 className="font-serif text-base font-semibold mb-1 leading-snug cursor-pointer hover:text-primary transition-colors"
                      onClick={() => paper.source === 'arxiv' ? navigate(`/arxiv/${encodeURIComponent(paper.source_id)}`) : window.open(paper.url, '_blank')}>
                      {paper.title}
                    </h3>
                    {paper.authors.length > 0 && (
                      <p className="text-xs text-muted-foreground mb-1 truncate">
                        <Users className="h-3 w-3 inline mr-1" />{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ` +${paper.authors.length - 3}` : ''}
                      </p>
                    )}
                    {paper.abstract && <p className="text-xs text-muted-foreground line-clamp-2">{paper.abstract}</p>}
                    {paper.fields_of_study.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1.5">
                        {paper.fields_of_study.slice(0, 3).map(f => (
                          <span key={f} className="text-[10px] px-1.5 py-0.5 rounded bg-secondary text-muted-foreground">{f}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-1 shrink-0">
                    <Button variant="ghost" size="icon" className={`h-7 w-7 ${isInCompare(paper) ? 'text-primary' : 'text-muted-foreground'}`}
                      onClick={() => toggleCompare(paper)} data-testid={`compare-toggle-${paper.source_id}`}>
                      <GitCompare className="h-3.5 w-3.5" />
                    </Button>
                    {paper.pdf_url && (
                      <Button variant="ghost" size="icon" asChild className="h-7 w-7 text-muted-foreground">
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

export default DiscoverPage;
