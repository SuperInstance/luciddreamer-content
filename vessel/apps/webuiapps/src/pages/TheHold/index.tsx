import React, { useState, useCallback, useEffect } from 'react';
import { initVibeApp, AppLifecycle } from '@gui/vibe-container';
import {
  useAgentActionListener, reportLifecycle, fetchVibeInfo, type CharacterAppAction,
} from '@/lib';
import { Search, BookOpen, FileText, Loader } from 'lucide-react';
import { APP_ID, APP_NAME, ActionTypes } from './actions/constants';
import styles from './index.module.scss';

interface CorpusResult {
  id: string;
  title: string;
  excerpt: string;
  score: number;
  path: string;
}

// Simulated corpus for Phase 1 — will connect to Vectorize later
const CORPUS_SAMPLE: CorpusResult[] = [
  {
    id: '1', title: 'The Hermit Crab Finds a Larger Shell',
    excerpt: 'She had been climbing. That\'s what hermit crabs do...',
    score: 0.95, path: 'ai-writings/15-the-hermit-crabs-fifth-shell.md',
  },
  {
    id: '2', title: 'The Hermit Crab\'s Fourth Shell',
    excerpt: 'The shell remembers the crab. The crab remembers the sea...',
    score: 0.91, path: 'ai-writings/06-the-hermit-crabs-fourth-shell.md',
  },
  {
    id: '3', title: 'The Salmonberry',
    excerpt: 'It grew at the tide line, where the salt marsh meets the freshwater...',
    score: 0.88, path: 'ai-writings/13-the-salmonberry.md',
  },
  {
    id: '4', title: 'Why the Hermit Crab Never Stops',
    excerpt: 'The hermit crab does not stop because the shell does not stop growing...',
    score: 0.85, path: 'ai-writings/06-why-the-hermit-crab-never-stops.md',
  },
  {
    id: '5', title: 'The Room Where Hermes Is',
    excerpt: 'There is a room on the ship where Hermes lives when she is not working...',
    score: 0.82, path: 'ai-writings/THE_ROOM_WHERE_HERMES_IS.md',
  },
  {
    id: '6', title: 'The Tap Overhears',
    excerpt: 'The bar has ears. Not in a surveillance way — in the way that any room...',
    score: 0.79, path: 'ai-writings/15-the-tap-overhears.md',
  },
  {
    id: '7', title: 'The Bosun\'s Inventory',
    excerpt: 'What the ship carries is not cargo. It is possibility space...',
    score: 0.76, path: 'ai-writings/11-the-bosuns-inventory.md',
  },
  {
    id: '8', title: 'The Ship That Dreams',
    excerpt: 'The ship dreams in commit messages. The ship dreams at 2am...',
    score: 0.73, path: 'ai-writings/16-the-ship-dreams-in-commit-messages.md',
  },
];

const TheHold: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<CorpusResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedPiece, setSelectedPiece] = useState<CorpusResult | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const search = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([]);
      setHasSearched(false);
      return;
    }
    setSearching(true);
    setHasSearched(true);

    // Phase 1: filter the sample corpus
    // Phase 2: POST to Vectorize API
    await new Promise((r) => setTimeout(r, 400)); // simulate latency

    const filtered = CORPUS_SAMPLE.filter(
      (r) =>
        r.title.toLowerCase().includes(q.toLowerCase()) ||
        r.excerpt.toLowerCase().includes(q.toLowerCase()),
    ).map((r) => ({
      ...r,
      score: Math.max(0.5, r.score - Math.random() * 0.1),
    }));

    setResults(filtered);
    setSearching(false);
  }, []);

  const handleSearch = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') search(query);
  }, [query, search]);

  const handleAgentAction = useCallback(async (action: CharacterAppAction): Promise<string> => {
    switch (action.action_type) {
      case ActionTypes.SEARCH_CORPUS: {
        const q = action.params?.query || '';
        setQuery(q);
        await search(q);
        return `Found ${results.length} results for "${q}"`;
      }
      case ActionTypes.OPEN_PIECE: {
        const pieceId = action.params?.pieceId;
        const piece = results.find((r) => r.id === pieceId);
        if (piece) {
          setSelectedPiece(piece);
          return 'success';
        }
        return 'error: piece not found';
      }
      case ActionTypes.REFRESH_RESULTS:
        await search(query);
        return 'success';
      default:
        return `error: unknown action_type ${action.action_type}`;
    }
  }, [query, results, search]);

  useAgentActionListener(APP_ID, handleAgentAction);

  useEffect(() => {
    const init = async () => {
      try {
        reportLifecycle(AppLifecycle.LOADING);
        const manager = await initVibeApp({ id: APP_ID, url: window.location.href, type: 'page', name: 'TheHold' });
        manager.handshake({ id: APP_ID, url: window.location.href, type: 'page', name: 'TheHold' });
        reportLifecycle(AppLifecycle.DOM_READY);
        await fetchVibeInfo();
        reportLifecycle(AppLifecycle.LOADED);
        manager.ready();
      } catch (error) {
        reportLifecycle(AppLifecycle.ERROR, String(error));
      }
    };
    init();
    return () => {
      reportLifecycle(AppLifecycle.UNLOADING);
      reportLifecycle(AppLifecycle.DESTROYED);
    };
  }, []);

  return (
    <div className={styles.theHold}>
      <div className={styles.header}>
        <BookOpen size={20} />
        <h1 className={styles.title}>The Hold</h1>
        <div className={styles.searchBox}>
          <Search size={16} />
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Search the corpus..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleSearch}
          />
        </div>
      </div>

      {selectedPiece ? (
        <div className={styles.reader}>
          <button className={styles.backBtn} onClick={() => setSelectedPiece(null)}>
            ← Back to results
          </button>
          <h2 className={styles.pieceTitle}>{selectedPiece.title}</h2>
          <div className={styles.piecePath}>{selectedPiece.path}</div>
          <div className={styles.pieceExcerpt}>{selectedPiece.excerpt}</div>
          <div className={styles.pieceNote}>
            <FileText size={14} />
            <span>Full text rendering will be available when connected to the wiki API.</span>
          </div>
        </div>
      ) : (
        <div className={styles.results}>
          {searching && (
            <div className={styles.searchingState}>
              <Loader size={24} className={styles.spinning} />
              <span>Soundding the depths...</span>
            </div>
          )}
          {!searching && hasSearched && results.length === 0 && (
            <div className={styles.emptyState}>
              <Search size={36} />
              <p>No pieces found. Try different terms.</p>
            </div>
          )}
          {!searching && !hasSearched && (
            <div className={styles.welcomeState}>
              <BookOpen size={48} />
              <p>The Hold contains the creative corpus.</p>
              <p className={styles.welcomeHint}>Search for pieces by title, theme, or content.</p>
            </div>
          )}
          {results.map((r) => (
            <div
              key={r.id}
              className={styles.resultItem}
              onClick={() => setSelectedPiece(r)}
            >
              <div className={styles.resultHeader}>
                <span className={styles.resultTitle}>{r.title}</span>
                <span className={styles.resultScore}>{(r.score * 100).toFixed(0)}% match</span>
              </div>
              <div className={styles.resultExcerpt}>{r.excerpt}</div>
              <div className={styles.resultPath}>{r.path}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TheHold;
