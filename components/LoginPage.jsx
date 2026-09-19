import React, { useState } from "react";

export function LoginPage({
  brandName = "Watermelon",
  onGoogleLogin = () => {},
  onLogin = (email, password, remember) => {},
  onForgotPassword = () => {},
  onCreateAccount = () => {},
  copyrightYear = 2026,
  footerLinks = [
    { label: "Privacy", href: "#" },
    { label: "Terms", href: "#" },
    { label: "Support", href: "#" },
  ],
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [mode, setMode] = useState("user"); // "user" | "admin" | "create"
  const [fullName, setFullName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      if (mode === "admin") {
        // Admin login API call
        const res = await fetch("/api/auth/admin/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (res.ok && data.access_token) {
          localStorage.setItem("pv_token", data.access_token);
          localStorage.setItem("pv_role", "ADMIN");
          localStorage.setItem("pv_user", JSON.stringify(data.user));
          if (onLogin) onLogin(email, password, remember);
          window.location.hash = "admin-dashboard";
        } else {
          setErrorMsg("Invalid administrator credentials. Access denied.");
        }
      } else if (mode === "create") {
        // Register API call
        const res = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, full_name: fullName }),
        });
        const data = await res.json();
        if (res.ok && data.access_token) {
          localStorage.setItem("pv_token", data.access_token);
          localStorage.setItem("pv_role", "USER");
          localStorage.setItem("pv_user", JSON.stringify(data.user));
          if (onCreateAccount) onCreateAccount();
          setMode("user");
        } else {
          setErrorMsg(data.error?.message || "Registration failed.");
        }
      } else {
        // Normal user login API call
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await res.json();
        if (res.ok && data.access_token) {
          localStorage.setItem("pv_token", data.access_token);
          localStorage.setItem("pv_role", data.role || "USER");
          localStorage.setItem("pv_user", JSON.stringify(data.user));
          if (remember) {
            localStorage.setItem("pv_remember_email", email);
          } else {
            localStorage.removeItem("pv_remember_email");
          }
          if (onLogin) onLogin(email, password, remember);
        } else {
          setErrorMsg(data.error?.message || "Invalid credentials.");
        }
      }
    } catch (err) {
      setErrorMsg("Failed to connect to authentication service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-between bg-slate-50 text-slate-900 antialiased p-4 sm:p-6 lg:p-8">
      {/* Top Brand Bar */}
      <div className="flex items-center justify-between max-w-5xl w-full mx-auto">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500 to-emerald-500 flex items-center justify-center text-white shadow-md font-bold text-xl">
            🍉
          </div>
          <div>
            <div className="font-extrabold text-lg tracking-tight text-slate-900 leading-none">
              {brandName}
            </div>
            <div className="text-[10px] uppercase font-mono tracking-widest text-emerald-600 font-semibold mt-0.5">
              Smart Vision Platform
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setMode(mode === "admin" ? "user" : "admin");
              setErrorMsg("");
            }}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 border ${
              mode === "admin"
                ? "bg-amber-100 text-amber-900 border-amber-300 shadow-sm"
                : "bg-white text-slate-700 border-slate-200 hover:bg-slate-100"
            }`}
          >
            <span>🛡️</span>
            <span>{mode === "admin" ? "Admin Mode Active" : "Admin Portal"}</span>
          </button>
        </div>
      </div>

      {/* Main Login Card */}
      <div className="max-w-md w-full mx-auto my-8 bg-white rounded-3xl border border-slate-200 shadow-xl p-8 sm:p-10 relative">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-rose-500 via-rose-400 to-emerald-500 flex items-center justify-center text-white mx-auto mb-4 text-2xl shadow-lg shadow-rose-500/20">
            {mode === "admin" ? "🛡️" : "🍉"}
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">
            {mode === "admin"
              ? "ADMIN ACCESS"
              : mode === "create"
              ? "Create your account"
              : `Sign in to ${brandName}`}
          </h1>
          <p className="text-xs text-slate-500 mt-1 font-medium">
            {mode === "admin"
              ? "Authorized administrator personnel only"
              : mode === "create"
              ? "Join the intelligent smart parking network"
              : "Welcome back! Please enter your details to sign in"}
          </p>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold text-center animate-shake">
            {errorMsg}
          </div>
        )}

        {/* Google Login Button (for normal users) */}
        {mode !== "admin" && (
          <>
            <button
              type="button"
              onClick={onGoogleLogin}
              className="w-full py-2.5 px-4 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-sm font-semibold shadow-sm flex items-center justify-center gap-3 transition"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>Continue with Google</span>
            </button>

            <div className="relative my-6 flex items-center justify-center">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200"></div>
              </div>
              <span className="relative bg-white px-3 text-xs uppercase font-mono font-bold text-slate-400">
                Or continue with email
              </span>
            </div>
          </>
        )}

        {/* Login / Register Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "create" && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              {mode === "admin" ? "Administrator Email" : "Email address"}
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={mode === "admin" ? "admin@parkvision.ai" : "you@example.com"}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold text-slate-700">
                {mode === "admin" ? "Administrator Password" : "Password"}
              </label>
              {mode === "user" && onForgotPassword && (
                <button
                  type="button"
                  onClick={onForgotPassword}
                  className="text-xs font-medium text-emerald-600 hover:text-emerald-700 hover:underline"
                >
                  Forgot password?
                </button>
              )}
            </div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none transition"
            />
          </div>

          {mode !== "admin" && mode !== "create" && (
            <div className="flex items-center">
              <input
                id="remember-checkbox"
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
              />
              <label
                htmlFor="remember-checkbox"
                className="ml-2 block text-xs text-slate-600 cursor-pointer select-none"
              >
                Remember me for 30 days
              </label>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-xl font-bold text-sm shadow-md transition flex items-center justify-center gap-2 ${
              mode === "admin"
                ? "bg-amber-600 hover:bg-amber-700 text-white shadow-amber-500/25"
                : "bg-gradient-to-r from-rose-500 to-emerald-600 hover:from-rose-600 hover:to-emerald-700 text-white shadow-emerald-500/25"
            }`}
          >
            {loading ? (
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : mode === "admin" ? (
              "LOGIN TO ADMIN CONSOLE"
            ) : mode === "create" ? (
              "CREATE ACCOUNT"
            ) : (
              "SIGN IN"
            )}
          </button>
        </form>

        {/* Toggle between Login, Create Account, and Admin */}
        <div className="mt-6 pt-5 border-t border-slate-100 text-center space-y-3">
          {mode === "admin" ? (
            <button
              type="button"
              onClick={() => {
                setMode("user");
                setErrorMsg("");
              }}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 underline"
            >
              ← Back to User Login
            </button>
          ) : mode === "create" ? (
            <p className="text-xs text-slate-600">
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("user");
                  setErrorMsg("");
                }}
                className="font-bold text-emerald-600 hover:text-emerald-700 underline ml-1"
              >
                Sign in
              </button>
            </p>
          ) : (
            <p className="text-xs text-slate-600">
              Don't have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("create");
                  setErrorMsg("");
                  if (onCreateAccount) onCreateAccount();
                }}
                className="font-bold text-emerald-600 hover:text-emerald-700 underline ml-1"
              >
                Create account
              </button>
            </p>
          )}
        </div>
      </div>

      {/* Footer Links & Copyright */}
      <div className="max-w-md w-full mx-auto text-center space-y-2">
        <div className="flex items-center justify-center gap-6 text-xs text-slate-500 font-medium">
          {footerLinks.map((link, idx) => (
            <a
              key={idx}
              href={link.href}
              className="hover:text-slate-900 transition underline-offset-4 hover:underline"
            >
              {link.label}
            </a>
          ))}
        </div>
        <div className="text-[11px] text-slate-400 font-mono">
          © {copyrightYear} {brandName}. All rights reserved.
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
