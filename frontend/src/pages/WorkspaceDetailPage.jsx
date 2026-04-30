import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { discoverAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Loader2, ArrowLeft, Trash2, ExternalLink, Calendar, Edit3,
  Check, X, FileText, Tag, MessageSquare, Download, Copy
} from 'lucide-react';
import { toast } from 'sonner';

const WorkspaceDetailPage = () => {
  const { wsId } = useParams();
  const navigate = useNavigate();
  const [workspace, setWorkspace] = useState(null);
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editNotes, setEditNotes] = useState('');
  const [editTags, setEditTags] = useState('');

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await discoverAPI.getWorkspace(wsId);
        setWorkspace(res.data);
        setPapers(res.data.papers || []);
      } catch { toast.error('Workspace not found'); navigate('/workspaces'); }
      finally { setLoading(false); }
    };
    fetch();
  }, [wsId, navigate]);

  const handleRemove = async (paperId) => {
    try {
      await discoverAPI.removePaper(wsId, paperId);
      setPapers(papers.filter(p => p.id !== paperId));
      toast.success('Removed');
    } catch { toast.error('Failed'); }
  };

  const startEdit = (paper) => {
    setEditingId(paper.id);
    setEditNotes(paper.notes || '');
    setEditTags(paper.tags || '');
  };

  const saveAnnotation = async (paperId) => {
    try {
      const res = await discoverAPI.annotatePaper(wsId, paperId, { notes: editNotes, tags: editTags });
      setPapers(papers.map(p => p.id === paperId ? res.data : p));
      setEditingId(null);
      toast.success('Annotation saved');
    } catch { toast.error('Failed'); }
  };

  const handleExport = async (format) => {
    const ids = papers.map(p => p.id);
    if (ids.length === 0) { toast.error('No papers to export'); return; }
    try {
      const res = await discoverAPI.exportPapers({ paper_ids: ids, format });
      navigator.clipboard.writeText(res.data.content);
      toast.success(`${format.toUpperCase()} copied to clipboard`);
    } catch { toast.error('Export failed'); }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background grain">
        <Header />
        <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-4xl mx-auto" data-testid="workspace-detail-page">
        <Button variant="ghost" size="sm" onClick={() => navigate('/workspaces')} className="mb-4 text-muted-foreground" data-testid="ws-back-btn">
          <ArrowLeft className="h-4 w-4 mr-1" /> Workspaces
        </Button>

        {workspace && (
          <div className="mb-6">
            <h1 className="font-serif text-2xl font-bold mb-0.5">{workspace.name}</h1>
            {workspace.description && <p className="text-sm text-muted-foreground">{workspace.description}</p>}
            <div className="flex gap-2 mt-3">
              <Button variant="outline" size="sm" onClick={() => handleExport('bibtex')} data-testid="export-bibtex-btn">
                <Copy className="h-3.5 w-3.5 mr-1" /> BibTeX
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport('markdown')} data-testid="export-md-btn">
                <Download className="h-3.5 w-3.5 mr-1" /> Markdown
              </Button>
            </div>
          </div>
        )}

        {papers.length === 0 ? (
          <Card className="p-10 text-center bg-card border-border/60" data-testid="empty-ws-papers">
            <FileText className="h-8 w-8 mx-auto mb-3 text-muted-foreground opacity-40" />
            <p className="text-sm text-muted-foreground mb-4">No papers in this workspace. Add papers from Discover or arXiv search.</p>
            <Button onClick={() => navigate('/discover')} data-testid="go-discover-btn">Search Papers</Button>
          </Card>
        ) : (
          <div className="space-y-3" data-testid="ws-papers-list">
            {papers.map((paper, idx) => (
              <Card key={paper.id}
                className="p-4 bg-card border-border/60 animate-in"
                style={{ animationDelay: `${idx * 30}ms` }}
                data-testid={`ws-paper-${paper.id}`}>
                <div className="flex gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{paper.source}</span>
                      {paper.year && <span className="text-xs text-muted-foreground"><Calendar className="h-3 w-3 inline mr-0.5" />{paper.year}</span>}
                    </div>
                    <h3 className="font-serif text-base font-semibold mb-1 leading-snug">{paper.title}</h3>
                    {paper.authors_str && <p className="text-xs text-muted-foreground mb-1">{paper.authors_str}</p>}

                    {/* Tags */}
                    {paper.tags && (
                      <div className="flex flex-wrap gap-1 mb-1.5">
                        {paper.tags.split(',').filter(Boolean).map(t => (
                          <span key={t} className="cat-pill text-[10px]"><Tag className="h-2.5 w-2.5 mr-0.5 inline" />{t.trim()}</span>
                        ))}
                      </div>
                    )}

                    {/* Notes */}
                    {paper.notes && editingId !== paper.id && (
                      <div className="p-2 bg-secondary/50 rounded text-xs text-muted-foreground mt-1.5 flex items-start gap-1.5">
                        <MessageSquare className="h-3 w-3 mt-0.5 shrink-0 text-primary" />
                        <span>{paper.notes}</span>
                      </div>
                    )}

                    {/* Edit annotation */}
                    {editingId === paper.id && (
                      <div className="mt-2 space-y-2 animate-in">
                        <textarea value={editNotes} onChange={e => setEditNotes(e.target.value)}
                          placeholder="Your notes on this paper..."
                          className="w-full p-2 text-xs rounded bg-secondary border border-border text-foreground resize-none h-20"
                          data-testid="annotation-notes-input" />
                        <Input value={editTags} onChange={e => setEditTags(e.target.value)}
                          placeholder="Tags (comma-separated)"
                          className="text-xs bg-secondary" data-testid="annotation-tags-input" />
                        <div className="flex gap-1.5">
                          <Button size="sm" className="h-7 text-xs" onClick={() => saveAnnotation(paper.id)} data-testid="save-annotation-btn">
                            <Check className="h-3 w-3 mr-0.5" /> Save
                          </Button>
                          <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => setEditingId(null)}>
                            <X className="h-3 w-3 mr-0.5" /> Cancel
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col gap-1 shrink-0">
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground"
                      onClick={() => startEdit(paper)} data-testid={`annotate-btn-${paper.id}`}>
                      <Edit3 className="h-3.5 w-3.5" />
                    </Button>
                    {paper.pdf_url && (
                      <Button variant="ghost" size="icon" asChild className="h-7 w-7 text-muted-foreground">
                        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer"><ExternalLink className="h-3.5 w-3.5" /></a>
                      </Button>
                    )}
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive"
                      onClick={() => handleRemove(paper.id)} data-testid={`remove-ws-paper-${paper.id}`}>
                      <Trash2 className="h-3.5 w-3.5" />
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

export default WorkspaceDetailPage;
