import React from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { ThumbsUp, ThumbsDown, ArrowUpRight, Quote } from 'lucide-react';

const sourceLabel = (s) => ({
  openalex: 'OpenAlex',
  semantic_scholar: 'Semantic Scholar',
  arxiv: 'arXiv',
}[s] || s || 'Source');

const scoreTone = (score) => {
  if (score >= 0.7) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
  if (score >= 0.45) return 'text-sky-400 border-sky-500/30 bg-sky-500/10';
  return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
};

const RecommendationCard = ({ rec, onOpen, onFeedback, feedback }) => {
  return (
    <Card
      className="group flex flex-col p-6 transition-all duration-300 hover:shadow-xl hover:-translate-y-0.5 border-border/60"
      data-testid={`recommendation-card-${rec.paper_id}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${scoreTone(rec.score)}`}>
          {(rec.score * 100).toFixed(0)}% match
        </div>
        <span className="text-[10px] uppercase tracking-wide px-2 py-0.5 rounded-md border border-border/60 text-muted-foreground" data-testid={`recommendation-source-${rec.paper_id}`}>
          {sourceLabel(rec.source)}
        </span>
      </div>

      <button
        onClick={() => onOpen(rec.paper_id)}
        className="text-left"
        data-testid={`recommendation-open-${rec.paper_id}`}
      >
        <h3 className="font-serif text-lg font-semibold mb-2 line-clamp-3 group-hover:text-primary transition-colors">
          {rec.title}
        </h3>
      </button>

      <div className="text-sm text-muted-foreground mb-3">
        {rec.authors?.length > 0 && (
          <p className="truncate">
            {rec.authors.slice(0, 2).join(', ')}
            {rec.authors.length > 2 && ` +${rec.authors.length - 2}`}
          </p>
        )}
        <div className="flex items-center gap-2 mt-1 flex-wrap">
          {rec.year && <span>{rec.year}</span>}
          {rec.venue && (<><span>·</span><span className="truncate max-w-[180px]">{rec.venue}</span></>)}
          {rec.citation_count > 0 && (
            <><span>·</span><span className="inline-flex items-center gap-1"><Quote className="h-3 w-3" />{rec.citation_count}</span></>
          )}
        </div>
      </div>

      {rec.reasons?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-4" data-testid={`recommendation-reasons-${rec.paper_id}`}>
          {rec.reasons.slice(0, 3).map((r, i) => (
            <span key={i} className="text-[11px] px-2 py-0.5 rounded-md bg-secondary/60 text-secondary-foreground border border-border/50">
              {r}
            </span>
          ))}
        </div>
      )}

      <div className="mt-auto flex items-center justify-between pt-3 border-t border-border/50">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onOpen(rec.paper_id)}
          data-testid={`recommendation-view-${rec.paper_id}`}
        >
          View <ArrowUpRight className="h-4 w-4 ml-1" />
        </Button>
        <div className="flex items-center gap-1">
          <Button
            variant={feedback === 'up' ? 'default' : 'ghost'}
            size="icon"
            className="h-8 w-8"
            onClick={() => onFeedback(rec.paper_id, 'up')}
            title="More like this"
            data-testid={`recommendation-thumbs-up-${rec.paper_id}`}
          >
            <ThumbsUp className="h-4 w-4" />
          </Button>
          <Button
            variant={feedback === 'down' ? 'default' : 'ghost'}
            size="icon"
            className="h-8 w-8"
            onClick={() => onFeedback(rec.paper_id, 'down')}
            title="Not relevant"
            data-testid={`recommendation-thumbs-down-${rec.paper_id}`}
          >
            <ThumbsDown className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default RecommendationCard;
