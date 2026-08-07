import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function LoginPage() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [isSubmitted, setIsSubmitted] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitted(true);
  }

  return (
    <section className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">Welcome back</p>
        <h1>Log in to SnipShare</h1>
        <p className="auth-intro">This is a visual placeholder only. It does not authenticate, save a token, or contact a server.</p>
        <form onSubmit={handleSubmit} className="form-stack">
          <label>Username<input required autoComplete="username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
          <label>Password<input required type="password" autoComplete="current-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          {isSubmitted && <p className="notice placeholder-notice">No login was attempted. Connect this form to your FastAPI login endpoint when it is ready.</p>}
          <button className="button full-width">Log in</button>
        </form>
        <p className="auth-switch">New here? <Link to="/register">Create an account</Link></p>
      </div>
    </section>
  );
}
