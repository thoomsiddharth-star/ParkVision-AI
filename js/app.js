/**
 * ParkVision AI - Application Controller
 * Handles SPA navigation, UI rendering, space selection, modal dialogs, and toasts.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Authentication & Session State
  let authState = {
    token: localStorage.getItem('pv_token') || null,
    role: localStorage.getItem('pv_role') || null,
    user: JSON.parse(localStorage.getItem('pv_user') || 'null')
  };

  // Navigation & View Routing
  const navLinks = document.querySelectorAll('[data-route]');
  const views = document.querySelectorAll('.page-view');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  let currentRoute = 'home';
  let selectedSpace = null;
  let activeFacility = window.parkingService ? window.parkingService.getLocationById('central-hub') : null;

  // Initialize Subsystems
  let cameraSim = null;
  let dashboardCharts = null;

  // Initialize App
  initAuthSystem();
  initRouter();
  initLiveParkingGrid();
  initMiniLotPreview();
  initFacilityCards();
  initDetailView();
  initEventListeners();
  updateLiveMetrics();

  // Initialize Charts & Camera when respective pages show or on start
  dashboardCharts = new window.DashboardCharts();
  dashboardCharts.init();

  // -------------------------------------------------------------
  // Authentication & Role-Based Access Control
  // -------------------------------------------------------------
  function initAuthSystem() {
    updateAuthUI();

    // Modal elements
    const authModal = document.getElementById('auth-modal');
    const openLoginBtn = document.getElementById('btn-open-login');
    const mobileOpenLoginBtn = document.getElementById('mobile-btn-open-login');
    const closeAuthModalBtn = document.getElementById('close-auth-modal-btn');
    const userLoginContainer = document.getElementById('user-login-container');
    const createAccountContainer = document.getElementById('create-account-container');
    const adminLoginContainer = document.getElementById('admin-login-container');
    const btnSwitchAdminMode = document.getElementById('btn-switch-admin-mode');
    const btnSwitchUserMode = document.getElementById('btn-switch-user-mode');
    const btnBackToMainLogin = document.getElementById('btn-back-to-main-login');
    const btnAdminSubmit = document.getElementById('btn-admin-submit');
    const btnUserSignin = document.getElementById('btn-user-signin');
    const btnLogout = document.getElementById('btn-logout');
    const adminLoginError = document.getElementById('admin-login-error');

    // Auth4 specific elements
    const btnGoogleLogin = document.getElementById('btn-google-login');
    const btnForgotPassword = document.getElementById('btn-forgot-password');
    const btnToCreateAccount = document.getElementById('btn-to-create-account');
    const btnBackToSignin = document.getElementById('btn-back-to-signin');
    const btnSubmitRegister = document.getElementById('btn-submit-register');
    const authRemember = document.getElementById('auth-remember');
    const linkPrivacy = document.getElementById('link-privacy');
    const linkTerms = document.getElementById('link-terms');
    const linkSupport = document.getElementById('link-support');

    // Restore remembered email if previously stored
    const rememberedEmail = localStorage.getItem('pv_remember_email');
    if (rememberedEmail) {
      const emailInput = document.getElementById('auth-email');
      if (emailInput) emailInput.value = rememberedEmail;
      if (authRemember) authRemember.checked = true;
    }

    function openModal(mode = 'user') {
      if (!authModal) return;
      authModal.classList.remove('hidden');
      authModal.classList.add('flex');
      if (mode === 'admin') {
        userLoginContainer.classList.add('hidden');
        if (createAccountContainer) createAccountContainer.classList.add('hidden');
        adminLoginContainer.classList.remove('hidden');
        if (adminLoginError) adminLoginError.classList.add('hidden');
      } else if (mode === 'create') {
        userLoginContainer.classList.add('hidden');
        if (createAccountContainer) createAccountContainer.classList.remove('hidden');
        adminLoginContainer.classList.add('hidden');
      } else {
        userLoginContainer.classList.remove('hidden');
        if (createAccountContainer) createAccountContainer.classList.add('hidden');
        adminLoginContainer.classList.add('hidden');
      }
    }

    function closeModal() {
      if (!authModal) return;
      authModal.classList.add('hidden');
      authModal.classList.remove('flex');
      if (adminLoginError) adminLoginError.classList.add('hidden');
    }

    if (openLoginBtn) openLoginBtn.addEventListener('click', () => openModal('user'));
    if (mobileOpenLoginBtn) mobileOpenLoginBtn.addEventListener('click', () => openModal('user'));
    if (closeAuthModalBtn) closeAuthModalBtn.addEventListener('click', closeModal);
    if (btnSwitchAdminMode) btnSwitchAdminMode.addEventListener('click', () => openModal('admin'));
    if (btnSwitchUserMode) btnSwitchUserMode.addEventListener('click', () => openModal('user'));
    if (btnBackToMainLogin) btnBackToMainLogin.addEventListener('click', () => openModal('user'));
    if (btnToCreateAccount) {
      btnToCreateAccount.addEventListener('click', () => {
        console.log("Create account");
        openModal('create');
      });
    }
    if (btnBackToSignin) btnBackToSignin.addEventListener('click', () => openModal('user'));

    // onGoogleLogin handler (Auth4 Spec)
    if (btnGoogleLogin) {
      btnGoogleLogin.addEventListener('click', () => {
        console.log("Google login");
        showToast("Connecting with Google Account (SSO)...", "info");
        setTimeout(() => {
          // Sign in demo google user
          const mockGoogleUser = {
            id: 888,
            email: "google.user@parkvision.ai",
            full_name: "Google Verified Driver",
            role: "USER",
            is_active: true
          };
          authState.token = "demo_google_jwt_token_" + Date.now();
          authState.role = "USER";
          authState.user = mockGoogleUser;
          localStorage.setItem('pv_token', authState.token);
          localStorage.setItem('pv_role', "USER");
          localStorage.setItem('pv_user', JSON.stringify(mockGoogleUser));
          updateAuthUI();
          closeModal();
          showToast("Successfully signed in via Google Account!", "success");
        }, 800);
      });
    }

    // onForgotPassword handler (Auth4 Spec)
    if (btnForgotPassword) {
      btnForgotPassword.addEventListener('click', () => {
        console.log("Forgot password");
        const email = document.getElementById('auth-email')?.value.trim() || "user@parkvision.ai";
        showToast(`Password reset link sent to ${email}`, "info");
      });
    }

    // onCreateAccount / Register Form Submit (Auth4 Spec)
    if (btnSubmitRegister) {
      btnSubmitRegister.addEventListener('click', async (e) => {
        e.preventDefault();
        const fullName = document.getElementById('reg-fullname')?.value.trim() || "Driver";
        const email = document.getElementById('reg-email')?.value.trim();
        const password = document.getElementById('reg-password')?.value;

        if (!email || !password) {
          showToast("Please provide both email and password.", "error");
          return;
        }

        try {
          const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name: fullName })
          });
          const data = await res.json();
          if (res.ok && data.access_token) {
            authState.token = data.access_token;
            authState.role = data.role;
            authState.user = data.user;
            localStorage.setItem('pv_token', data.access_token);
            localStorage.setItem('pv_role', data.role);
            localStorage.setItem('pv_user', JSON.stringify(data.user));
            updateAuthUI();
            closeModal();
            showToast(`Account created! Welcome, ${fullName}!`, "success");
          } else {
            showToast(data.error?.message || "Account creation failed.", "error");
          }
        } catch (err) {
          showToast("Failed to connect to registration server.", "error");
        }
      });
    }

    // Footer Links: Privacy, Terms, Support (Auth4 Spec)
    if (linkPrivacy) {
      linkPrivacy.addEventListener('click', (e) => {
        e.preventDefault();
        showToast("Watermelon Privacy Policy: Zero tracking of vehicle telemetry without consent.", "info");
      });
    }
    if (linkTerms) {
      linkTerms.addEventListener('click', (e) => {
        e.preventDefault();
        showToast("Terms of Service: Standard municipal parking reservation regulations apply.", "info");
      });
    }
    if (linkSupport) {
      linkSupport.addEventListener('click', (e) => {
        e.preventDefault();
        showToast("Support: Contact support@parkvision.ai or 24/7 Operations Desk.", "info");
      });
    }

    // Admin Login Submission
    if (btnAdminSubmit) {
      btnAdminSubmit.addEventListener('click', async (e) => {
        e.preventDefault();
        const email = document.getElementById('admin-email').value.trim();
        const password = document.getElementById('admin-password').value;

        if (adminLoginError) adminLoginError.classList.add('hidden');

        try {
          const res = await fetch('/api/auth/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          });

          const data = await res.json();
          if (res.ok && data.access_token) {
            authState.token = data.access_token;
            authState.role = data.role;
            authState.user = data.user;

            localStorage.setItem('pv_token', data.access_token);
            localStorage.setItem('pv_role', data.role);
            localStorage.setItem('pv_user', JSON.stringify(data.user));

            updateAuthUI();
            closeModal();
            showToast('Welcome Administrator! Admin session active.', 'success');
            
            // Navigate to Admin Dashboard
            window.location.hash = 'admin-dashboard';
          } else {
            if (adminLoginError) {
              adminLoginError.classList.remove('hidden');
            } else {
              showToast('Invalid administrator credentials. Access denied.', 'error');
            }
          }
        } catch (err) {
          if (adminLoginError) adminLoginError.classList.remove('hidden');
        }
      });
    }

    // Normal User Login Submission: onLogin(email, password, remember)
    if (btnUserSignin) {
      btnUserSignin.addEventListener('click', async (e) => {
        e.preventDefault();
        const email = document.getElementById('auth-email').value.trim();
        const password = document.getElementById('auth-password').value;
        const remember = authRemember ? authRemember.checked : false;

        console.log("Login", email, password, remember);

        try {
          const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          });

          const data = await res.json();
          if (res.ok && data.access_token) {
            authState.token = data.access_token;
            authState.role = data.role;
            authState.user = data.user;

            localStorage.setItem('pv_token', data.access_token);
            localStorage.setItem('pv_role', data.role);
            localStorage.setItem('pv_user', JSON.stringify(data.user));

            if (remember) {
              localStorage.setItem('pv_remember_email', email);
            } else {
              localStorage.removeItem('pv_remember_email');
            }

            updateAuthUI();
            closeModal();
            showToast(`Signed in as ${data.user.full_name || data.user.email}`, 'info');
          } else {
            showToast(data.error?.message || 'Login failed. Please check your credentials.', 'error');
          }
        } catch (err) {
          showToast('Failed to connect to authentication server.', 'error');
        }
      });
    }

    // Logout
    if (btnLogout) {
      btnLogout.addEventListener('click', () => {
        authState = { token: null, role: null, user: null };
        localStorage.removeItem('pv_token');
        localStorage.removeItem('pv_role');
        localStorage.removeItem('pv_user');

        updateAuthUI();
        showToast('Logged out. Admin session invalidated.', 'info');
        
        if (window.location.hash.includes('admin')) {
          window.location.hash = 'home';
        }
      });
    }
  }

  function updateAuthUI() {
    const userBadge = document.getElementById('user-badge');
    const userRoleBadge = document.getElementById('user-role-badge');
    const userEmailLabel = document.getElementById('user-email-label');
    const btnOpenLogin = document.getElementById('btn-open-login');
    const adminNavGroup = document.getElementById('admin-nav-group');
    const mobileAdminLinks = document.getElementById('mobile-admin-links');

    if (authState.token && authState.user) {
      if (btnOpenLogin) btnOpenLogin.classList.add('hidden');
      if (userBadge) userBadge.classList.remove('hidden');

      if (userEmailLabel) userEmailLabel.textContent = authState.user.email;

      if (authState.role === 'ADMIN') {
        if (userRoleBadge) {
          userRoleBadge.textContent = 'ADMIN';
          userRoleBadge.className = 'px-1.5 py-0.5 rounded font-mono font-bold text-[10px] bg-amber-100 text-amber-800 border border-amber-300';
        }
        if (adminNavGroup) adminNavGroup.classList.remove('hidden');
        if (mobileAdminLinks) mobileAdminLinks.classList.remove('hidden');
      } else {
        if (userRoleBadge) {
          userRoleBadge.textContent = 'USER';
          userRoleBadge.className = 'px-1.5 py-0.5 rounded font-mono font-bold text-[10px] bg-blue-100 text-blue-700';
        }
        if (adminNavGroup) adminNavGroup.classList.add('hidden');
        if (mobileAdminLinks) mobileAdminLinks.classList.add('hidden');
      }
    } else {
      if (btnOpenLogin) btnOpenLogin.classList.remove('hidden');
      if (userBadge) userBadge.classList.add('hidden');
      if (adminNavGroup) adminNavGroup.classList.add('hidden');
      if (mobileAdminLinks) mobileAdminLinks.classList.add('hidden');
    }
  }

  // -------------------------------------------------------------
  // Router Functionality with Role-Based Route Protection
  // -------------------------------------------------------------
  function initRouter() {
    function navigateTo(route) {
      if (!route) route = 'home';

      // ROLE-BASED ROUTE PROTECTION
      if (route.startsWith('admin')) {
        if (authState.role !== 'ADMIN' || !authState.token) {
          showToast('Access Denied: Administrator authentication required.', 'error');
          const authModal = document.getElementById('auth-modal');
          if (authModal) {
            authModal.classList.remove('hidden');
            authModal.classList.add('flex');
            document.getElementById('user-login-container')?.classList.add('hidden');
            document.getElementById('admin-login-container')?.classList.remove('hidden');
          }
          window.location.hash = 'home';
          route = 'home';
        }
      }

      currentRoute = route;

      views.forEach(v => {
        if (v.id === `view-${route}`) {
          v.classList.remove('hidden');
        } else {
          v.classList.add('hidden');
        }
      });

      // Update active nav styling
      navLinks.forEach(link => {
        if (link.getAttribute('data-route') === route) {
          link.classList.add('text-blue-600', 'font-semibold');
          link.classList.remove('text-slate-600');
        } else {
          link.classList.remove('text-blue-600', 'font-semibold');
          link.classList.add('text-slate-600');
        }
      });

      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });

      // Close mobile menu
      if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
      }

      // Page-specific initialization
      if (route === 'ai') {
        if (!cameraSim) {
          cameraSim = new window.CameraSimulator('aiCameraCanvas');
        }
      } else if (route === 'details') {
        renderDetailView();
      } else if (route === 'navigate') {
        renderNavigationView();
      } else if (route === 'admin-dashboard') {
        renderAdminDashboard();
      } else if (route === 'admin-cameras') {
        renderAdminCameras();
      } else if (route === 'admin-users') {
        renderAdminUsers();
      }
    }

    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const route = link.getAttribute('data-route');
        navigateTo(route);
        window.location.hash = route;
      });
    });

    // Handle hash change
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.replace('#', '') || 'home';
      navigateTo(hash);
    });

    // Check initial hash
    const initialHash = window.location.hash.replace('#', '') || 'home';
    navigateTo(initialHash);
  }

  // Admin View Renderers & Handlers
  async function renderAdminDashboard() {
    if (!authState.token) return;
    try {
      const res = await fetch('/api/admin/dashboard', {
        headers: { 'Authorization': `Bearer ${authState.token}` }
      });
      if (res.ok) {
        const data = await res.json();
        document.getElementById('admin-stat-lots').textContent = data.total_lots;
        document.getElementById('admin-stat-spaces').textContent = data.total_spaces;
        document.getElementById('admin-stat-occupied').textContent = data.occupied_spaces;
        document.getElementById('admin-stat-available').textContent = data.available_spaces;
        document.getElementById('admin-stat-cameras').textContent = `${data.active_cameras}/${data.total_cameras}`;
        document.getElementById('admin-stat-incidents').textContent = `${data.open_security_incidents} Open`;
      }
    } catch (e) {
      console.warn('Failed to load admin dashboard telemetry:', e);
    }
  }

  // Admin space override handlers
  const btnLock = document.getElementById('btn-admin-space-lock');
  const btnMaintenance = document.getElementById('btn-admin-space-maintenance');
  const btnUnlock = document.getElementById('btn-admin-space-unlock');

  async function handleAdminSpaceAction(action) {
    const spaceId = document.getElementById('admin-space-id-input').value;
    const resultDiv = document.getElementById('admin-space-action-result');

    try {
      const res = await fetch(`/api/admin/spaces/${spaceId}/status?status_action=${action}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authState.token}` }
      });
      const data = await res.json();
      if (res.ok) {
        resultDiv.classList.remove('hidden');
        resultDiv.textContent = `✅ Space #${data.id} (${data.space_number}) status set to ${data.status}`;
        showToast(`Space ${data.space_number} updated to ${data.status}`, 'success');
        if (window.parkingService) window.parkingService.fetchLiveParkingData();
      } else {
        showToast(data.detail?.message || 'Admin action failed.', 'error');
      }
    } catch (e) {
      showToast('Failed to execute admin action.', 'error');
    }
  }

  if (btnLock) btnLock.addEventListener('click', () => handleAdminSpaceAction('LOCK'));
  if (btnMaintenance) btnMaintenance.addEventListener('click', () => handleAdminSpaceAction('MAINTENANCE'));
  if (btnUnlock) btnUnlock.addEventListener('click', () => handleAdminSpaceAction('UNLOCK'));

  async function renderAdminCameras() {
    if (!authState.token) return;
    const container = document.getElementById('admin-cameras-list-container');
    if (!container) return;

    try {
      const res = await fetch('/api/admin/cameras', {
        headers: { 'Authorization': `Bearer ${authState.token}` }
      });
      if (res.ok) {
        const cams = await res.json();
        container.innerHTML = cams.map(c => `
          <div class="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
            <div class="flex items-center justify-between mb-2">
              <span class="font-mono text-xs font-bold text-slate-800">${c.camera_number}</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-100 text-emerald-800">${c.status}</span>
            </div>
            <h4 class="font-bold text-sm text-slate-900 mb-1">${c.name}</h4>
            <div class="text-xs text-slate-500 font-mono space-y-1">
              <div>Detected Cars: <span class="font-bold text-slate-800">${c.cars_detected}</span></div>
              <div>Spaces Monitored: <span class="font-bold text-slate-800">${c.spaces_detected}</span></div>
              <div>AI Confidence: <span class="font-bold text-blue-600">${c.ai_confidence}%</span></div>
            </div>
          </div>
        `).join('');
      }
    } catch (e) {}
  }

  async function renderAdminUsers() {
    if (!authState.token) return;
    const tbody = document.getElementById('admin-users-table-body');
    if (!tbody) return;

    try {
      const res = await fetch('/api/admin/users', {
        headers: { 'Authorization': `Bearer ${authState.token}` }
      });
      if (res.ok) {
        const users = await res.json();
        tbody.innerHTML = users.map(u => `
          <tr class="hover:bg-slate-50">
            <td class="px-4 py-3">${u.id}</td>
            <td class="px-4 py-3 font-semibold text-slate-900">${u.email}</td>
            <td class="px-4 py-3">${u.full_name || '—'}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${u.role === 'ADMIN' ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'}">${u.role}</span>
            </td>
            <td class="px-4 py-3">
              <span class="text-emerald-600 font-bold">${u.is_active ? 'Active' : 'Disabled'}</span>
            </td>
            <td class="px-4 py-3 text-right">
              <button class="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] rounded" onclick="alert('User #${u.id} account details inspected.')">Inspect</button>
            </td>
          </tr>
        `).join('');
      }
    } catch (e) {}
  }

  // -------------------------------------------------------------
  // Mini-Lot Preview (Landing Page Hero)
  // -------------------------------------------------------------
  function initMiniLotPreview() {
    const previewContainer = document.getElementById('hero-mini-lot');
    if (!previewContainer) return;

    renderMiniLot();

    // Subscribe to parkingService to animate spaces live
    window.parkingService.subscribe((eventType, data) => {
      if (eventType === 'spaces_updated') {
        renderMiniLot();
      }
    });
  }

  function renderMiniLot() {
    const previewContainer = document.getElementById('hero-mini-lot');
    if (!previewContainer) return;

    const spaces = window.parkingService.getSpaces().slice(0, 10); // First 10 spaces
    previewContainer.innerHTML = spaces.map(space => {
      const isAvail = space.status === 'AVAILABLE';
      const isUncertain = space.status === 'UNCERTAIN';
      const bgColor = isAvail ? 'bg-emerald-500' : (isUncertain ? 'bg-amber-400' : 'bg-rose-500');
      const textColor = isAvail ? 'text-emerald-950' : 'text-white';
      const statusText = isAvail ? 'FREE' : (isUncertain ? 'BUSY?' : 'OCC');

      return `
        <div class="flex flex-col items-center justify-between p-2 rounded-lg border ${isAvail ? 'border-emerald-300 bg-emerald-50/70' : 'border-rose-200 bg-rose-50/60'} transition-all duration-300">
          <div class="text-[11px] font-mono font-bold text-slate-700">${space.id}</div>
          <div class="w-full h-8 flex items-center justify-center my-1 rounded ${bgColor} ${textColor} text-[10px] font-bold shadow-sm">
            ${statusText}
          </div>
          <div class="w-1.5 h-1.5 rounded-full ${isAvail ? 'bg-emerald-500 animate-pulse' : 'bg-rose-400'}"></div>
        </div>
      `;
    }).join('');
  }

  // -------------------------------------------------------------
  // Live Parking Grid (A01 to A40)
  // -------------------------------------------------------------
  function initLiveParkingGrid() {
    const gridContainer = document.getElementById('parking-grid-container');
    if (!gridContainer) return;

    renderParkingGrid();

    // Subscribe to updates
    window.parkingService.subscribe((eventType, data) => {
      if (eventType === 'spaces_updated') {
        renderParkingGrid();
        updateLiveMetrics();
        // If a space was changed, show a quick toast if relevant
        if (data.changedSpaces && data.changedSpaces.length > 0) {
          const change = data.changedSpaces[0];
          if (change.newStatus === 'AVAILABLE') {
            showToast(`🟢 Space ${change.space.id} is now AVAILABLE`, 'info');
          } else if (change.newStatus === 'OCCUPIED') {
            showToast(`🔴 Space ${change.space.id} was just OCCUPIED`, 'info');
          }
        }
      }
    });
  }

  function renderParkingGrid(filter = 'all') {
    const gridContainer = document.getElementById('parking-grid-container');
    if (!gridContainer) return;

    const spaces = window.parkingService.getSpaces();
    const filteredSpaces = spaces.filter(space => {
      if (filter === 'available') return space.status === 'AVAILABLE';
      if (filter === 'occupied') return space.status === 'OCCUPIED';
      return true;
    });

    gridContainer.innerHTML = filteredSpaces.map(space => {
      const isAvail = space.status === 'AVAILABLE';
      const isUncertain = space.status === 'UNCERTAIN';
      const isSelected = selectedSpace && selectedSpace.id === space.id;

      let statusBadge = '';
      let borderClass = 'border-slate-200 bg-white hover:border-blue-400';
      let iconColor = 'text-slate-400';

      if (isAvail) {
        borderClass = 'border-emerald-300 bg-emerald-50/40 hover:border-emerald-500';
        statusBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-100 text-emerald-800">🟢 AVAILABLE</span>';
        iconColor = 'text-emerald-600';
      } else if (isUncertain) {
        borderClass = 'border-amber-300 bg-amber-50/40 hover:border-amber-500';
        statusBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-800">🟡 UNCERTAIN</span>';
        iconColor = 'text-amber-600';
      } else {
        borderClass = 'border-rose-200 bg-rose-50/30 hover:border-rose-400';
        statusBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-rose-100 text-rose-800">🔴 OCCUPIED</span>';
        iconColor = 'text-rose-500';
      }

      if (isSelected) {
        borderClass += ' ring-2 ring-blue-600 border-blue-600 shadow-md';
      }

      return `
        <div class="parking-slot-card rounded-xl border p-4 cursor-pointer flex flex-col justify-between ${borderClass}" data-space-id="${space.id}">
          <div class="flex items-center justify-between mb-2">
            <span class="font-mono text-base font-bold text-slate-800">${space.id}</span>
            <span class="text-xs font-medium text-slate-500">${space.zone.split(' ')[0]}</span>
          </div>

          <div class="my-2 flex items-center justify-center h-14 rounded-lg ${isAvail ? 'bg-emerald-100/60' : (isUncertain ? 'bg-amber-100/60' : 'bg-rose-100/60')}">
            <svg class="w-8 h-8 ${iconColor}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />
            </svg>
          </div>

          <div class="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
            ${statusBadge}
            <span class="text-[11px] text-slate-400 font-mono">${space.lastUpdated}</span>
          </div>
        </div>
      `;
    }).join('');

    // Attach click handlers to slots
    gridContainer.querySelectorAll('.parking-slot-card').forEach(card => {
      card.addEventListener('click', () => {
        const spaceId = card.getAttribute('data-space-id');
        openSpaceModal(spaceId);
      });
    });
  }

  // -------------------------------------------------------------
  // Space Details Modal / Drawer Handler
  // -------------------------------------------------------------
  function openSpaceModal(spaceId) {
    const space = window.parkingService.getSpaceById(spaceId);
    if (!space) return;

    const modal = document.getElementById('space-detail-modal');
    if (!modal) return;

    document.getElementById('modal-space-id').textContent = space.id;
    document.getElementById('modal-zone').textContent = space.zone;
    document.getElementById('modal-last-updated').textContent = space.lastUpdated;

    const statusBadgeEl = document.getElementById('modal-status-badge');
    const actionContainerEl = document.getElementById('modal-action-container');
    const warningEl = document.getElementById('modal-occupied-warning');

    if (space.status === 'AVAILABLE') {
      statusBadgeEl.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800';
      statusBadgeEl.textContent = '🟢 AVAILABLE';
      warningEl.classList.add('hidden');

      actionContainerEl.innerHTML = `
        <button id="modal-select-btn" class="w-full py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition shadow-sm flex items-center justify-center gap-2">
          <span>Select Space</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        </button>
      `;

      document.getElementById('modal-select-btn').addEventListener('click', () => {
        selectedSpace = space;
        closeSpaceModal();
        showToast(`Parking space ${space.id} selected.`, 'success');
        renderParkingGrid();
        
        // Show Navigate CTA button in bottom bar
        const selectionBanner = document.getElementById('selected-space-bar');
        if (selectionBanner) {
          selectionBanner.classList.remove('hidden');
          document.getElementById('selected-space-label').textContent = `Space ${space.id} selected`;
        }
      });
    } else {
      statusBadgeEl.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800';
      statusBadgeEl.textContent = '🔴 OCCUPIED';
      warningEl.classList.remove('hidden');
      document.getElementById('modal-occupied-msg').textContent = `Space ${space.id} is currently occupied.`;

      actionContainerEl.innerHTML = `
        <button id="modal-filter-avail-btn" class="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm transition shadow-sm flex items-center justify-center gap-2">
          <span>View available spaces</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        </button>
      `;

      document.getElementById('modal-filter-avail-btn').addEventListener('click', () => {
        closeSpaceModal();
        // Highlight available filter
        const filterBtns = document.querySelectorAll('.grid-filter-btn');
        filterBtns.forEach(btn => {
          if (btn.getAttribute('data-filter') === 'available') {
            btn.classList.add('bg-blue-600', 'text-white');
            btn.classList.remove('bg-white', 'text-slate-700');
          } else {
            btn.classList.remove('bg-blue-600', 'text-white');
            btn.classList.add('bg-white', 'text-slate-700');
          }
        });
        renderParkingGrid('available');
        showToast('Filtered to available parking spaces', 'info');
      });
    }

    modal.classList.remove('hidden');
    modal.classList.add('flex');
  }

  function closeSpaceModal() {
    const modal = document.getElementById('space-detail-modal');
    if (modal) {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }
  }

  const closeModalBtn = document.getElementById('close-modal-btn');
  if (closeModalBtn) closeModalBtn.addEventListener('click', closeSpaceModal);

  // Close modal when backdrop clicked
  const modalElem = document.getElementById('space-detail-modal');
  if (modalElem) {
    modalElem.addEventListener('click', (e) => {
      if (e.target === modalElem) closeSpaceModal();
    });
  }

  // -------------------------------------------------------------
  // Live Metrics Display
  // -------------------------------------------------------------
  function updateLiveMetrics() {
    const stats = window.parkingService.getStats();

    // Live Parking page metrics
    const totalEl = document.getElementById('stat-total-spaces');
    const availEl = document.getElementById('stat-available-spaces');
    const occEl = document.getElementById('stat-occupied-spaces');
    const rateEl = document.getElementById('stat-occupancy-rate');
    const timeEl = document.getElementById('stat-last-updated');

    if (totalEl) totalEl.textContent = stats.total;
    if (availEl) availEl.textContent = stats.available;
    if (occEl) occEl.textContent = stats.occupied;
    if (rateEl) rateEl.textContent = `${stats.occupancyRate}%`;
    if (timeEl) timeEl.textContent = `Last updated: ${stats.lastUpdatedText}`;

    // Admin Dashboard metrics
    const dashTotal = document.getElementById('dash-total-spaces');
    const dashAvail = document.getElementById('dash-available-spaces');
    const dashOcc = document.getElementById('dash-current-occupancy');
    const dashRate = document.getElementById('dash-occupancy-rate');

    if (dashTotal) dashTotal.textContent = stats.total;
    if (dashAvail) dashAvail.textContent = stats.available;
    if (dashOcc) dashOcc.textContent = stats.occupied;
    if (dashRate) dashRate.textContent = `${stats.occupancyRate}%`;

    // Activity log rendering on dashboard
    renderActivityLogs();
  }

  function renderActivityLogs() {
    const logContainer = document.getElementById('operator-activity-logs');
    if (!logContainer || !window.parkingService) return;

    const logs = window.parkingService.activityLogs;
    logContainer.innerHTML = logs.map(log => {
      const isOccupied = log.action === 'Occupied';
      return `
        <div class="flex items-center justify-between p-3 rounded-lg border border-slate-100 hover:bg-slate-50 text-xs">
          <div class="flex items-center gap-3">
            <span class="w-2 h-2 rounded-full ${isOccupied ? 'bg-rose-500' : 'bg-emerald-500'}"></span>
            <div>
              <span class="font-bold text-slate-800">Space ${log.spaceId}</span>
              <span class="text-slate-500 ml-1.5">${log.action}: ${log.vehicle}</span>
            </div>
          </div>
          <span class="font-mono text-slate-400 text-[11px]">${log.time}</span>
        </div>
      `;
    }).join('');
  }

  // -------------------------------------------------------------
  // Find Parking: Nearby Facilities Cards
  // -------------------------------------------------------------
  function initFacilityCards() {
    const container = document.getElementById('facilities-list-container');
    if (!container) return;

    renderFacilityCards();

    // Search and sort filter
    const searchInput = document.getElementById('search-facility-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        renderFacilityCards(e.target.value);
      });
    }
  }

  function renderFacilityCards(searchQuery = '') {
    const container = document.getElementById('facilities-list-container');
    if (!container) return;

    const locations = window.parkingService.getLocations();
    const filtered = locations.filter(loc => {
      if (!searchQuery) return true;
      return loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
             loc.address.toLowerCase().includes(searchQuery.toLowerCase());
    });

    container.innerHTML = filtered.map(loc => {
      const isFull = loc.availableSpaces === 0;
      return `
        <div class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
          <div>
            <div class="flex items-start justify-between mb-2">
              <div>
                <h3 class="font-bold text-lg text-slate-900">${loc.name}</h3>
                <p class="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
                  <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                  ${loc.address}
                </p>
              </div>
              <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${isFull ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'}">
                ${loc.status}
              </span>
            </div>

            <!-- Stats Bar -->
            <div class="grid grid-cols-3 gap-2 my-4 p-3 rounded-xl bg-slate-50 border border-slate-100 text-center">
              <div>
                <div class="text-lg font-bold text-emerald-600">${loc.availableSpaces}</div>
                <div class="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Available</div>
              </div>
              <div>
                <div class="text-lg font-bold text-rose-500">${loc.occupiedSpaces}</div>
                <div class="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Occupied</div>
              </div>
              <div>
                <div class="text-lg font-bold text-slate-800">${loc.occupancyRate}%</div>
                <div class="text-[11px] text-slate-500 uppercase tracking-wider font-semibold">Occupancy</div>
              </div>
            </div>

            <div class="flex items-center justify-between text-xs text-slate-500 py-1 mb-4">
              <span class="font-medium text-slate-700">📍 ${loc.distance} away (${loc.estimatedTime})</span>
              <span class="font-medium text-blue-600">${loc.rate}</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3 pt-3 border-t border-slate-100">
            <button class="view-facility-btn py-2.5 px-4 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 font-semibold text-xs transition" data-facility-id="${loc.id}">
              View Parking
            </button>
            <button class="nav-facility-btn py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition shadow-sm" data-facility-id="${loc.id}">
              Navigate
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Attach click listeners
    container.querySelectorAll('.view-facility-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-facility-id');
        activeFacility = window.parkingService.getLocationById(id);
        window.location.hash = 'details';
      });
    });

    container.querySelectorAll('.nav-facility-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-facility-id');
        activeFacility = window.parkingService.getLocationById(id);
        window.location.hash = 'navigate';
      });
    });
  }

  // -------------------------------------------------------------
  // Parking Details Page (Section 8)
  // -------------------------------------------------------------
  function initDetailView() {
    renderDetailView();
  }

  function renderDetailView() {
    if (!activeFacility) activeFacility = window.parkingService.getLocationById('central-hub');
    const stats = window.parkingService.getStats();

    const nameEl = document.getElementById('details-facility-name');
    const addressEl = document.getElementById('details-facility-address');
    const totalEl = document.getElementById('details-total-spaces');
    const availEl = document.getElementById('details-available');
    const occEl = document.getElementById('details-occupied');
    const rateEl = document.getElementById('details-occupancy-rate');

    if (nameEl) nameEl.textContent = activeFacility.name;
    if (addressEl) addressEl.textContent = activeFacility.address;
    if (totalEl) totalEl.textContent = activeFacility.id === 'central-hub' ? stats.total : activeFacility.totalSpaces;
    if (availEl) availEl.textContent = activeFacility.id === 'central-hub' ? stats.available : activeFacility.availableSpaces;
    if (occEl) occEl.textContent = activeFacility.id === 'central-hub' ? stats.occupied : activeFacility.occupiedSpaces;
    if (rateEl) rateEl.textContent = `${activeFacility.id === 'central-hub' ? stats.occupancyRate : activeFacility.occupancyRate}%`;

    // Render interactive bay layout for details view
    renderDetailsLayout();

    // Update selection indicator
    updateDetailsSelectionUI();
  }

  function renderDetailsLayout() {
    const container = document.getElementById('details-bays-layout');
    if (!container) return;

    const spaces = window.parkingService.getSpaces();
    container.innerHTML = spaces.map(space => {
      const isAvail = space.status === 'AVAILABLE';
      const isSelected = selectedSpace && selectedSpace.id === space.id;
      let bg = isAvail ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-rose-500 opacity-60 cursor-not-allowed';
      if (isSelected) bg = 'bg-blue-600 ring-4 ring-blue-300';

      return `
        <button class="details-slot-btn h-12 rounded-lg text-white font-mono text-xs font-bold transition flex flex-col items-center justify-center p-1 ${bg}" data-space-id="${space.id}" ${!isAvail ? 'disabled' : ''}>
          <span>${space.id}</span>
          <span class="text-[9px] font-sans font-normal">${isAvail ? 'FREE' : 'BUSY'}</span>
        </button>
      `;
    }).join('');

    container.querySelectorAll('.details-slot-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-space-id');
        const res = window.parkingService.selectSpace(id);
        if (res.success) {
          selectedSpace = res.space;
          updateDetailsSelectionUI();
          renderDetailsLayout();
          showToast(`Parking space ${id} selected.`, 'success');
        }
      });
    });
  }

  function updateDetailsSelectionUI() {
    const labelEl = document.getElementById('details-selected-status-label');
    const navBtn = document.getElementById('details-navigate-btn');

    if (selectedSpace) {
      if (labelEl) labelEl.textContent = `Space ${selectedSpace.id} selected`;
      if (navBtn) {
        navBtn.removeAttribute('disabled');
        navBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      }
    } else {
      if (labelEl) labelEl.textContent = 'Please select an available parking bay';
      if (navBtn) {
        navBtn.setAttribute('disabled', 'true');
        navBtn.classList.add('opacity-50', 'cursor-not-allowed');
      }
    }
  }

  // -------------------------------------------------------------
  // Navigation Screen (Section 7)
  // -------------------------------------------------------------
  function renderNavigationView() {
    if (!activeFacility) activeFacility = window.parkingService.getLocationById('central-hub');
    const stats = window.parkingService.getStats();

    const destNameEl = document.getElementById('nav-destination-name');
    const destAddrEl = document.getElementById('nav-destination-address');
    const distEl = document.getElementById('nav-distance-text');
    const timeEl = document.getElementById('nav-time-text');
    const availEl = document.getElementById('nav-available-text');
    const spaceBadgeEl = document.getElementById('nav-selected-space-badge');
    const externalLink = document.getElementById('nav-external-maps-btn');

    if (destNameEl) destNameEl.textContent = activeFacility.name;
    if (destAddrEl) destAddrEl.textContent = activeFacility.address;
    if (distEl) distEl.textContent = activeFacility.distance;
    if (timeEl) timeEl.textContent = activeFacility.estimatedTime;
    
    const availableCount = activeFacility.id === 'central-hub' ? stats.available : activeFacility.availableSpaces;
    if (availEl) availEl.textContent = `${availableCount} spaces available`;

    if (spaceBadgeEl) {
      if (selectedSpace) {
        spaceBadgeEl.textContent = `Assigned Bay: ${selectedSpace.id} (${selectedSpace.zone})`;
        spaceBadgeEl.classList.remove('hidden');
      } else {
        spaceBadgeEl.classList.add('hidden');
      }
    }

    // Google Maps External URL
    if (externalLink) {
      const gmapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${activeFacility.lat},${activeFacility.lng}`;
      externalLink.href = gmapsUrl;
    }
  }

  // -------------------------------------------------------------
  // Event Listeners & Interactive Controls
  // -------------------------------------------------------------
  function initEventListeners() {
    // Mobile menu toggle
    if (mobileMenuBtn && mobileMenu) {
      mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
      });
    }

    // Live Parking Grid filter tabs
    const filterBtns = document.querySelectorAll('.grid-filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => {
          b.classList.remove('bg-blue-600', 'text-white');
          b.classList.add('bg-white', 'text-slate-700');
        });
        btn.classList.add('bg-blue-600', 'text-white');
        btn.classList.remove('bg-white', 'text-slate-700');
        renderParkingGrid(btn.getAttribute('data-filter'));
      });
    });

    // Simulation play/pause toggle button
    const simToggleBtn = document.getElementById('sim-toggle-btn');
    if (simToggleBtn) {
      simToggleBtn.addEventListener('click', () => {
        if (window.parkingService.isSimulationRunning()) {
          window.parkingService.stopSimulation();
          simToggleBtn.innerHTML = `
            <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path></svg>
            <span>Resume Simulation</span>
          `;
          showToast('Simulation paused', 'info');
        } else {
          window.parkingService.startSimulation();
          simToggleBtn.innerHTML = `
            <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>Pause Simulation</span>
          `;
          showToast('Simulation resumed', 'info');
        }
      });
    }

    // Manual simulation pulse buttons
    const simArriveBtn = document.getElementById('sim-arrival-btn');
    if (simArriveBtn) {
      simArriveBtn.addEventListener('click', () => {
        window.parkingService.triggerRandomChange();
        showToast('Simulated vehicle arrival', 'info');
      });
    }

    // Camera AI page controls
    const cam01Btn = document.getElementById('cam-switch-01');
    const cam02Btn = document.getElementById('cam-switch-02');
    if (cam01Btn && cam02Btn) {
      cam01Btn.addEventListener('click', () => {
        if (cameraSim) cameraSim.setCamera('CAM-01');
        cam01Btn.classList.add('bg-blue-600', 'text-white');
        cam01Btn.classList.remove('bg-slate-700', 'text-slate-300');
        cam02Btn.classList.remove('bg-blue-600', 'text-white');
        cam02Btn.classList.add('bg-slate-700', 'text-slate-300');
      });
      cam02Btn.addEventListener('click', () => {
        if (cameraSim) cameraSim.setCamera('CAM-02');
        cam02Btn.classList.add('bg-blue-600', 'text-white');
        cam02Btn.classList.remove('bg-slate-700', 'text-slate-300');
        cam01Btn.classList.remove('bg-blue-600', 'text-white');
        cam01Btn.classList.add('bg-slate-700', 'text-slate-300');
      });
    }

    const bboxToggle = document.getElementById('toggle-bbox-chk');
    if (bboxToggle) {
      bboxToggle.addEventListener('change', (e) => {
        if (cameraSim) cameraSim.toggleBoundingBoxes(e.target.checked);
      });
    }

    const confToggle = document.getElementById('toggle-conf-chk');
    if (confToggle) {
      confToggle.addEventListener('change', (e) => {
        if (cameraSim) cameraSim.toggleConfidence(e.target.checked);
      });
    }

    const scanToggle = document.getElementById('toggle-scan-chk');
    if (scanToggle) {
      scanToggle.addEventListener('change', (e) => {
        if (cameraSim) cameraSim.toggleScanline(e.target.checked);
      });
    }

    // Start navigation button click handler
    const startNavBtn = document.getElementById('start-navigation-action');
    if (startNavBtn) {
      startNavBtn.addEventListener('click', () => {
        const statusBox = document.getElementById('nav-guidance-active-box');
        if (statusBox) {
          statusBox.classList.remove('hidden');
          startNavBtn.textContent = 'Navigation in Progress...';
          startNavBtn.classList.add('bg-emerald-600', 'hover:bg-emerald-700');
          showToast('Turn-by-turn guidance started', 'success');
        }
      });
    }

    // Navigate to parking from Details page
    const detailsNavBtn = document.getElementById('details-navigate-btn');
    if (detailsNavBtn) {
      detailsNavBtn.addEventListener('click', () => {
        window.location.hash = 'navigate';
      });
    }

    // Navigate button from selected-space banner
    const bannerNavBtn = document.getElementById('banner-navigate-btn');
    if (bannerNavBtn) {
      bannerNavBtn.addEventListener('click', () => {
        window.location.hash = 'navigate';
      });
    }
  }

  // -------------------------------------------------------------
  // Toast Notifications
  // -------------------------------------------------------------
  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const borderColor = type === 'success' ? 'border-emerald-500' : (type === 'error' ? 'border-rose-500' : 'border-blue-500');
    toast.className = `toast-msg flex items-center gap-3 bg-slate-900/95 text-white px-4 py-3 rounded-xl border-l-4 ${borderColor} shadow-xl backdrop-blur-md text-sm font-medium`;
    
    toast.innerHTML = `
      <span>${message}</span>
      <button class="text-slate-400 hover:text-white text-xs ml-auto">✕</button>
    `;

    toast.querySelector('button').addEventListener('click', () => {
      toast.remove();
    });

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  window.showToast = showToast;
});
