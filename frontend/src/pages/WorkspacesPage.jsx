import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { discoverAPI } from '../lib/api';
import Header from '../components/Header';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Loader2, FolderOpen, Plus, Trash2, FileText, Calendar,
  Edit3, Check, X, ExternalLink, Tag, MessageSquare
} from 'lucide-react';
import { toast } from 'sonner';

const WorkspacesPage = () => {
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    discoverAPI.listWorkspaces().then(r => setWorkspaces(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    try {
      const res = await discoverAPI.createWorkspace({ name: newName, description: newDesc });
      setWorkspaces([res.data, ...workspaces]);
      setNewName(''); setNewDesc(''); setCreating(false);
      toast.success('Workspace created');
    } catch { toast.error('Failed'); }
  };

  const handleDelete = async (id) => {
    try {
      await discoverAPI.deleteWorkspace(id);
      setWorkspaces(workspaces.filter(w => w.id !== id));
      toast.success('Deleted');
    } catch { toast.error('Failed'); }
  };

  return (
    <div className="min-h-screen bg-background grain">
      <Header />
      <main className="container py-8 px-4 md:px-8 max-w-4xl mx-auto" data-testid="workspaces-page">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-serif text-3xl font-bold flex items-center gap-2.5">
              <FolderOpen className="h-7 w-7" /> Workspaces
            </h1>
            <p className="text-muted-foreground text-sm">Organize papers into research projects</p>
          </div>
          <Button onClick={() => setCreating(!creating)} variant={creating ? 'outline' : 'default'} size="sm" data-testid="new-workspace-btn">
            {creating ? <X className="h-4 w-4 mr-1" /> : <Plus className="h-4 w-4 mr-1" />}
            {creating ? 'Cancel' : 'New'}
          </Button>
        </div>

        {creating && (
          <Card className="p-4 bg-card border-border/60 mb-5 animate-in" data-testid="create-workspace-form">
            <Input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Workspace name"
              className="mb-2 bg-secondary" data-testid="workspace-name-input" />
            <Input value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="Description (optional)"
              className="mb-3 bg-secondary" data-testid="workspace-desc-input" />
            <Button onClick={handleCreate} size="sm" disabled={!newName.trim()} data-testid="workspace-create-btn">
              <Check className="h-4 w-4 mr-1" /> Create
            </Button>
          </Card>
        )}

        {loading ? (
          <div className="flex justify-center py-20"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
        ) : workspaces.length === 0 ? (
          <Card className="p-12 text-center bg-card border-border/60" data-testid="empty-workspaces">
            <FolderOpen className="h-10 w-10 mx-auto mb-3 text-muted-foreground opacity-40" />
            <h2 className="font-serif text-xl font-semibold mb-2">No workspaces yet</h2>
            <p className="text-muted-foreground text-sm mb-5">Create a workspace to organize your research papers.</p>
            <Button onClick={() => setCreating(true)} data-testid="create-first-ws-btn">Create Workspace</Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3" data-testid="workspace-list">
            {workspaces.map((ws, idx) => (
              <Card key={ws.id}
                className="p-4 bg-card border-border/60 hover:border-primary/30 cursor-pointer transition-all animate-in"
                style={{ animationDelay: `${idx * 40}ms` }}
                onClick={() => navigate(`/workspaces/${ws.id}`)}
                data-testid={`workspace-${ws.id}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-serif text-lg font-semibold mb-0.5">{ws.name}</h3>
                    {ws.description && <p className="text-xs text-muted-foreground line-clamp-2">{ws.description}</p>}
                    <p className="text-[10px] text-muted-foreground mt-2 flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {ws.updated_at ? new Date(ws.updated_at).toLocaleDateString() : 'Recently'}
                    </p>
                  </div>
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive shrink-0"
                    onClick={(e) => { e.stopPropagation(); handleDelete(ws.id); }}
                    data-testid={`delete-ws-${ws.id}`}>
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default WorkspacesPage;
