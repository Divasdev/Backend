import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PostCard from '../components/PostCard';
import { demoPosts } from '../data/demoPosts';

export default function FeedPage() {
  const [language, setLanguage] = useState('All languages');

  const languages = useMemo(
    () => ['All languages', ...new Set(demoPosts.map((post) => post.language).sort())],
    [],
  );
  const visiblePosts = language === 'All languages' ? demoPosts : demoPosts.filter((post) => post.language === language);

  return (
    <div className="feed-page">
      <section className="hero">
        <div>
          <p className="eyebrow">The developer’s little library</p>
          <h1>Share the snippet<br /><em>you’ll reuse tomorrow.</em></h1>
          <p className="hero-copy">Useful code, shared without the noise. Browse a growing collection of small solutions from the community.</p>
        </div>
        <Link className="button hero-button" to="/register">Join the community <span>→</span></Link>
      </section>
      <section className="feed-toolbar" aria-label="Feed controls">
        <div><h2>Latest snippets</h2><span>Static preview data — no API connected</span></div>
        <label className="filter-control">Filter by language
          <select value={language} onChange={(event) => setLanguage(event.target.value)}>
            {languages.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
      </section>
      <p className="placeholder-note">This is display-only sample content. Replace it with data from your FastAPI API when you build the backend.</p>
      {visiblePosts.length === 0 && <div className="empty-state"><h2>No snippets in this language yet.</h2><p>Try another filter.</p></div>}
      <div className="post-list">
        {visiblePosts.map((post) => <PostCard key={post.id} post={post} />)}
      </div>
    </div>
  );
}
