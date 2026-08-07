import { Link, NavLink, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="header-content">
          <Link className="brand" to="/" aria-label="SnipShare home">
            <span className="brand-mark">&lt;/&gt;</span>
            <span>SnipShare</span>
          </Link>
          <nav className="main-nav" aria-label="Main navigation">
            <NavLink to="/" end>Explore</NavLink>
          </nav>
          <div className="auth-nav">
            <NavLink to="/login">Log in</NavLink>
            <NavLink className="button small-button" to="/register">Join SnipShare</NavLink>
          </div>
        </div>
      </header>
      <main className="page-content"><Outlet /></main>
      <footer className="site-footer">Built for sharing small, useful pieces of code.</footer>
    </div>
  );
}
