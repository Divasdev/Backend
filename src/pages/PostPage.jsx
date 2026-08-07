import { Link, useParams } from 'react-router-dom';
import { demoPosts } from '../data/demoPosts';

function formatDate(value) {
  return new Intl.DateTimeFormat('en', { month: 'long', day: 'numeric', year: 'numeric' }).format(new Date(value));
}

export default function PostPage() {
  const { id } = useParams();
  const post = demoPosts.find((item) => item.id === id);

  if (!post) return <div className="empty-state"><h2>Snippet not found.</h2><p>This static preview only includes the sample snippets on the home page.</p><Link className="button" to="/">Back to feed</Link></div>;
  return (
    <article className="detail-page">
      <Link className="back-link" to="/">← All snippets</Link>
      <div className="detail-header">
        <div><div className="post-card-meta"><span className="language-pill">{post.language}</span><span>Shared {formatDate(post.created_at)}</span></div><h1>{post.title}</h1>{post.description && <p>{post.description}</p>}</div>
      </div>
      <div className="code-panel"><div className="code-panel-bar"><span>{post.language}</span><span>snippet</span></div><pre><code>{post.code}</code></pre></div>
      <p className="placeholder-note detail-placeholder">Voting, editing, and deletion are intentionally unavailable until your FastAPI backend provides those endpoints.</p>
    </article>
  );
}
