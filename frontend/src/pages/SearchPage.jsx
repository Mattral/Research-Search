import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { paperAPI } from '../lib/api';
import { useAuth } from '../hooks/useAuth';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  Search, 
  Loader2, 
  Heart, 
  ExternalLink, 
  Calendar, 
  Users, 
  Building,
  Filter,
  X
} from 'lucide-react';
import { toast } from 'sonner';

const SearchPage = () => {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useState({
    title: '',
    author: '',
    year: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  // Load initial papers
  useEffect(() => {
    const loadInitialPapers = async () => {
      setLoading(true);
      try {
        const response = await paperAPI.browse(30);
        setPapers(response.data);
      } catch (error) {
        console.error('Failed to load papers:', error);
      } finally {
        setLoading(false);
      }
    };
    loadInitialPapers();
  }, []);

  const handleSearch = useCallback(async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setHasSearched(true);

    try {
      const params = {};
      if (searchParams.title) params.title = searchParams.title;
      if (searchParams.author) params.author = searchParams.author;
      if (searchParams.year) params.year = parseInt(searchParams.year);
      params.limit = 50;

      const response = await paperAPI.search(params);
      setPapers(response.data);
      
      if (response.data.length === 0) {
        toast.info('No papers found. Try different search terms.');
      }
    } catch (error) {
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  const handleLike = async (paperId, isLiked) => {
    try {
      if (isLiked) {
        await paperAPI.unlikePaper(paperId);
      } else {
        await paperAPI.likePaper(paperId);
      }
      
      setPapers((prev) =>
        prev.map((p) =>
          p.paper_id === paperId ? { ...p, is_liked: !isLiked } : p
        )
      );
      
      toast.success(isLiked ? 'Removed from favorites' : 'Added to favorites');
    } catch (error) {
      toast.error('Failed to update favorite');
    }
  };

  const handleViewPaper = async (paperId) => {
    try {
      await paperAPI.viewPaper(paperId);
    } catch (error) {
      console.error('Failed to track view:', error);
    }
    navigate(`/paper/${encodeURIComponent(paperId)}`);
  };

  const clearFilters = () => {
    setSearchParams({ title: '', author: '', year: '' });
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container py-8 px-4 md:px-8" data-testid="search-page">
        {/* Welcome Message */}
        {user && !hasSearched && (
          <div className="mb-8 animate-in">
            <h1 className="font-serif text-3xl md:text-4xl font-bold mb-2">
              Welcome back, {user.full_name || user.username}
            </h1>
            <p className="text-muted-foreground">
              Discover research papers that match your interests
            </p>
          </div>
        )}

        {/* Search Bar */}
        <div className="mb-8">
          <form onSubmit={handleSearch} className="flex flex-col gap-4">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search by paper title..."
                  value={searchParams.title}
                  onChange={(e) => setSearchParams({ ...searchParams, title: e.target.value })}
                  className="pl-10 h-12"
                  data-testid="search-title-input"
                />
              </div>
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => setShowFilters(!showFilters)}
                className="h-12"
                data-testid="filter-toggle-btn"
              >
                <Filter className="h-5 w-5" />
              </Button>
              <Button type="submit" className="h-12 px-6" disabled={loading} data-testid="search-btn">
                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Search'}
              </Button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="flex flex-wrap gap-4 p-4 bg-secondary/50 rounded-lg animate-in" data-testid="filters-panel">
                <div className="flex-1 min-w-[200px]">
                  <label className="text-sm font-medium text-muted-foreground mb-1 block">
                    Author
                  </label>
                  <Input
                    type="text"
                    placeholder="Author name..."
                    value={searchParams.author}
                    onChange={(e) => setSearchParams({ ...searchParams, author: e.target.value })}
                    data-testid="search-author-input"
                  />
                </div>
                <div className="w-32">
                  <label className="text-sm font-medium text-muted-foreground mb-1 block">
                    Year
                  </label>
                  <Input
                    type="number"
                    placeholder="2024"
                    value={searchParams.year}
                    onChange={(e) => setSearchParams({ ...searchParams, year: e.target.value })}
                    data-testid="search-year-input"
                  />
                </div>
                <Button 
                  type="button" 
                  variant="ghost" 
                  onClick={clearFilters}
                  className="self-end"
                >
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              </div>
            )}
          </form>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : papers.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground">
              {hasSearched ? 'No papers found' : 'Start searching for papers'}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-6 max-w-4xl mx-auto" data-testid="papers-list">
            {papers.map((paper, index) => (
              <Card
                key={paper.paper_id}
                className="group relative bg-white border border-border/60 p-6 hover:border-stone-300 hover:shadow-lg transition-all duration-300"
                style={{ animationDelay: `${index * 50}ms` }}
                data-testid={`paper-card-${paper.paper_id}`}
              >
                <div className="flex justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Title */}
                    <h3 
                      className="font-serif text-xl font-semibold mb-2 cursor-pointer hover:text-primary transition-colors line-clamp-2"
                      onClick={() => handleViewPaper(paper.paper_id)}
                      data-testid={`paper-title-${paper.paper_id}`}
                    >
                      {paper.title}
                    </h3>

                    {/* Metadata */}
                    <div className="flex flex-wrap gap-3 text-sm text-muted-foreground mb-3">
                      {paper.authors && paper.authors.length > 0 && (
                        <span className="flex items-center gap-1">
                          <Users className="h-4 w-4" strokeWidth={1.5} />
                          {paper.authors.slice(0, 3).join(', ')}
                          {paper.authors.length > 3 && ` +${paper.authors.length - 3}`}
                        </span>
                      )}
                      {paper.year && (
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" strokeWidth={1.5} />
                          {paper.year}
                        </span>
                      )}
                      {paper.venue && (
                        <span className="flex items-center gap-1">
                          <Building className="h-4 w-4" strokeWidth={1.5} />
                          {paper.venue}
                        </span>
                      )}
                    </div>

                    {/* Abstract */}
                    {paper.abstract && (
                      <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed">
                        {paper.abstract}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2 shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleLike(paper.paper_id, paper.is_liked)}
                      className={paper.is_liked ? 'text-red-500 hover:text-red-600' : ''}
                      data-testid={`like-btn-${paper.paper_id}`}
                    >
                      <Heart 
                        className="h-5 w-5" 
                        fill={paper.is_liked ? 'currentColor' : 'none'}
                        strokeWidth={1.5}
                      />
                    </Button>
                    {paper.url && (
                      <Button
                        variant="ghost"
                        size="icon"
                        asChild
                      >
                        <a href={paper.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-5 w-5" strokeWidth={1.5} />
                        </a>
                      </Button>
                    )}
                  </div>
                </div>

                {/* Citation Count Badge */}
                {paper.citation_count > 0 && (
                  <div className="absolute top-4 right-4 px-2 py-1 bg-secondary text-xs font-medium rounded-full">
                    {paper.citation_count} citations
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default SearchPage;
