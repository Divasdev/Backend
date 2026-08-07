import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function RegisterPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [isSubmitted, setIsSubmitted] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitted(true);
  }

  return (
    <section className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">Make it useful</p>
        <h1>Join SnipShare</h1>
        <p className="auth-intro">This is a visual placeholder only. Your future FastAPI backend will create accounts and store passwords securely.</p>
        <form onSubmit={handleSubmit} className="form-stack">
          <label>Username<input required minLength="2" autoComplete="username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
          <label>Email address<input required type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password<input required minLength="4" type="password" autoComplete="new-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          {isSubmitted && <p className="notice placeholder-notice">No account was created. Connect this form to your FastAPI registration endpoint when it is ready.</p>}
          <button className="button full-width">Create account</button>
        </form>
        <p className="auth-switch">Already a member? <Link to="/login">Log in</Link></p>
      </div>
    </section>
  );
}
