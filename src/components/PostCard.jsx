import { Link } from 'react-router-dom';

function formatDate(value) {
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
}

export default function PostCard({ post }) {
  return (
    <article className="post-card">
      <div className="vote-stack" aria-label={`${post.vote_count} votes`}>
        <span aria-hidden="true">▲</span>
        <strong>{post.vote_count}</strong>
        <span aria-hidden="true">▼</span>
      </div>
      <div className="post-card-main">
        <div className="post-card-meta"><span className="language-pill">{post.language}</span><span>{formatDate(post.created_at)}</span></div>
        <h2><Link to={`/posts/${post.id}`}>{post.title}</Link></h2>
        {post.description && <p>{post.description}</p>}
        <pre><code>{post.code}</code></pre>
        <Link className="read-link" to={`/posts/${post.id}`}>View snippet <span>→</span></Link>
      </div>
    </article>
  );
}
