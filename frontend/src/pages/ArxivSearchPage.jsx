import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { arxivAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Search, Loader2, Bookmark, BookmarkCheck, ExternalLink,
  Calendar, Users, Tag, ChevronLeft, ChevronRight, SlidersHorizontal, X
} from 'lucide-react';
import { toast } from 'sonner';

const ArxivSearchPage = () => {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [query, setQuery] = useState('');
  const [searchField, setSearchField] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [page, setPage] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const pageSize = 20;
  const navigate = useNavigate();

  useEffect(() => {
    arxivAPI.categories().then(r => setCategories(r.data)).catch(() => {});
    handleSearch(null, 0);
  }, []);

  const handleSearch = useCallback(async (e, startPage = 0) => {
    if (e) e.preventDefault();
    setLoading(true);
    setPage(startPage);
    try {
      const params = {
        query: query || 'machine learning',
        search_field: searchField,
        start: startPage * pageSize,
        max_results: pageSize,
        sort_by: sortBy,
        sort_order: 'descending',
      };
      if (selectedCategory) params.category = selectedCategory;
      const res = await arxivAPI.search(params);
      setPapers(res.data.papers);
      setTotalResults(res.data.total_results);
    } catch {
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  }, [query, searchField, selectedCategory, sortBy]);

  const handleSave = async (paper) => {
    try {
      if (paper.is_saved) {
        await arxivAPI.unsave(paper.arxiv_id);
        setPapers(p => p.map(pp => pp.arxiv_id === paper.arxiv_id ? { ...pp, is_saved: false } : pp));
        toast.success('Removed from reading list');
      } else {
        await arxivAPI.save({
          arxiv_id: paper.arxiv_id, title: paper.title, authors: paper.authors,
          summary: paper.summary, primary_category: paper.primary_category,
          published: paper.published, pdf_url: paper.pdf_url,
        });
        setPapers(p => p.map(pp => pp.arxiv_id === paper.arxiv_id ? { ...pp, is_saved: true } : pp));
        toast.success('Saved to reading list');
      }
    } catch { toast.error('Failed to update'); }
  };

  const totalPages = Math.ceil(Math.min(totalResults, 1000) / pageSize);

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-5xl mx-auto" data-testid="arxiv-search-page">
        <div className="mb-8">
          <h1 className="font-serif text-3xl md:text-4xl font-bold mb-1 tracking-tight">
            arXiv Explorer
          </h1>
          <p className="text-muted-foreground text-sm">
            Search {totalResults > 0 ? `${totalResults.toLocaleString()} papers on` : ''} arXiv.org
          </p>
        </div>

        {/* Search */}
        <form onSubmit={(e) => handleSearch(e, 0)} className="mb-6 space-y-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={query} onChange={e => setQuery(e.target.value)}
                placeholder="Search papers, authors, topics..."
                className="pl-10 h-11 bg-secondary border-border"
                data-testid="arxiv-search-input"
              />
            </div>
            <Button type="button" variant="outline" onClick={() => setShowFilters(!showFilters)} className="h-11" data-testid="arxiv-filters-btn">
              <SlidersHorizontal className="h-4 w-4" />
            </Button>
            <Button type="submit" className="h-11 px-6" disabled={loading} data-testid="arxiv-search-btn">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
            </Button>
          </div>

          {showFilters && (
            <div className="p-4 bg-secondary/60 rounded-lg border border-border/50 space-y-3 animate-in" data-testid="arxiv-filters-panel">
              <div className="flex flex-wrap gap-3">
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">Search in</label>
                  <select value={searchField} onChange={e => setSearchField(e.target.value)}
                    className="h-9 px-3 rounded-md bg-background border border-border text-sm text-foreground" data-testid="arxiv-field-select">
                    <option value="all">All fields</option>
                    <option value="ti">Title</option>
                    <option value="au">Author</option>
                    <option value="abs">Abstract</option>
                    <option value="cat">Category</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">Sort by</label>
                  <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                    className="h-9 px-3 rounded-md bg-background border border-border text-sm text-foreground" data-testid="arxiv-sort-select">
                    <option value="relevance">Relevance</option>
                    <option value="submittedDate">Date submitted</option>
                    <option value="lastUpdatedDate">Last updated</option>
                  </select>
                </div>
                {selectedCategory && (
                  <div className="flex items-end">
                    <Button type="button" variant="ghost" size="sm" onClick={() => setSelectedCategory('')}>
                      <X className="h-3 w-3 mr-1" /> Clear category
                    </Button>
                  </div>
                )}
              </div>
              <div className="flex flex-wrap gap-1.5">
                {categories.slice(0, 20).map(cat => (
                  <button key={cat.code} type="button"
                    className={`cat-pill ${selectedCategory === cat.code ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(selectedCategory === cat.code ? '' : cat.code)}
                    data-testid={`cat-${cat.code}`}>
                    {cat.code}
                  </button>
                ))}
              </div>
            </div>
          )}
        </form>

        {/* Results */}
        {loading ? (
          <div className="space-y-4">{[1,2,3].map(i => <div key={i} className="skeleton h-32 rounded-lg" />)}</div>
        ) : papers.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <Search className="h-10 w-10 mx-auto mb-3 opacity-40" />
            <p>No papers found. Try a different query.</p>
          </div>
        ) : (
          <>
            <div className="space-y-3" data-testid="arxiv-results">
              {papers.map((paper, idx) => (
                <Card key={paper.arxiv_id}
                  className="p-5 bg-card border-border/60 hover:border-primary/30 transition-all duration-200 animate-in"
                  style={{ animationDelay: `${idx * 40}ms` }}
                  data-testid={`arxiv-paper-${paper.arxiv_id}`}>
                  <div className="flex gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start gap-2 mb-1.5">
                        {paper.primary_category && (
                          <span className="cat-pill shrink-0 mt-0.5">{paper.primary_category}</span>
                        )}
                        {paper.year && (
                          <span className="text-xs text-muted-foreground flex items-center gap-1 shrink-0 mt-1">
                            <Calendar className="h-3 w-3" />{paper.year}
                          </span>
                        )}
                      </div>
                      <h3 className="font-serif text-lg font-semibold mb-1.5 leading-snug cursor-pointer hover:text-primary transition-colors"
                        onClick={() => navigate(`/arxiv/${encodeURIComponent(paper.arxiv_id)}`)}
                        data-testid={`arxiv-title-${paper.arxiv_id}`}>
                        {paper.title}
                      </h3>
                      {paper.authors.length > 0 && (
                        <p className="text-xs text-muted-foreground mb-2 flex items-center gap-1">
                          <Users className="h-3 w-3 shrink-0" />
                          <span className="truncate">{paper.authors.slice(0, 4).join(', ')}{paper.authors.length > 4 ? ` +${paper.authors.length - 4}` : ''}</span>
                        </p>
                      )}
                      {paper.summary && (
                        <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">{paper.summary}</p>
                      )}
                    </div>
                    <div className="flex flex-col gap-1.5 shrink-0">
                      <Button variant="ghost" size="icon" onClick={() => handleSave(paper)}
                        className={paper.is_saved ? 'text-primary' : 'text-muted-foreground'}
                        data-testid={`save-btn-${paper.arxiv_id}`}>
                        {paper.is_saved ? <BookmarkCheck className="h-4 w-4" /> : <Bookmark className="h-4 w-4" />}
                      </Button>
                      {paper.pdf_url && (
                        <Button variant="ghost" size="icon" asChild className="text-muted-foreground">
                          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-3 mt-8" data-testid="pagination">
                <Button variant="outline" size="sm" disabled={page === 0}
                  onClick={() => handleSearch(null, page - 1)} data-testid="prev-page-btn">
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm text-muted-foreground">
                  Page {page + 1} of {totalPages}
                </span>
                <Button variant="outline" size="sm" disabled={page >= totalPages - 1}
                  onClick={() => handleSearch(null, page + 1)} data-testid="next-page-btn">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default ArxivSearchPage;
