/**
 * VIBEUP MAIN SCRIPT
 * Handles real-time micro-interactions, theme toggles, likes, follows, comments, and modals.
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initLikeButtons();
  initFollowButtons();
  initCommentForms();
  initDeleteComments();
  initComposerFeatures();
  initShareButtons();
  initKeyboardShortcuts();
  initModals();
  initToasts();
});

// -------------------------------------------------------------
// CSRF TOKEN UTILITY
// -------------------------------------------------------------
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// -------------------------------------------------------------
// THEME SWITCHER
// -------------------------------------------------------------
function initTheme() {
  const themeToggles = document.querySelectorAll('.theme-toggle-btn');
  const htmlEl = document.documentElement;

  // Retrieve current preference from storage or attribute
  const savedTheme = localStorage.getItem('vibeup_theme') || htmlEl.getAttribute('data-theme') || 'dark';
  applyTheme(savedTheme);

  themeToggles.forEach(btn => {
    btn.addEventListener('click', () => {
      const currentTheme = htmlEl.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);

      // Save to server if possible
      fetch('/api/toggle-theme/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ theme: newTheme })
      }).catch(err => console.log('Theme sync error:', err));
    });
  });

  function applyTheme(theme) {
    htmlEl.setAttribute('data-theme', theme);
    localStorage.setItem('vibeup_theme', theme);

    themeToggles.forEach(btn => {
      const iconSpan = btn.querySelector('.theme-icon');
      if (iconSpan) {
        iconSpan.textContent = theme === 'dark' ? '☀️' : '🌙';
      }
      const labelSpan = btn.querySelector('.theme-label');
      if (labelSpan) {
        labelSpan.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
      }
    });
  }
}

// -------------------------------------------------------------
// LIKE / UNLIKE SYSTEM (Real-time AJAX)
// -------------------------------------------------------------
function initLikeButtons() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-like');
    if (!btn) return;
    e.preventDefault();

    const postId = btn.getAttribute('data-post-id');
    if (!postId) return;

    try {
      btn.style.pointerEvents = 'none';
      const response = await fetch(`/post/${postId}/like/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });

      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      if (response.ok) {
        const data = await response.json();
        const countSpan = btn.querySelector('.like-count');
        const iconSvg = btn.querySelector('svg');

        if (data.liked) {
          btn.classList.add('liked');
          if (iconSvg) iconSvg.style.transform = 'scale(1.35)';
        } else {
          btn.classList.remove('liked');
          if (iconSvg) iconSvg.style.transform = 'scale(0.85)';
        }

        setTimeout(() => {
          if (iconSvg) iconSvg.style.transform = 'scale(1)';
        }, 200);

        if (countSpan) {
          countSpan.textContent = data.likes_count;
        }
      }
    } catch (err) {
      console.error('Like toggle error:', err);
    } finally {
      btn.style.pointerEvents = 'auto';
    }
  });
}

// -------------------------------------------------------------
// FOLLOW / UNFOLLOW SYSTEM (Real-time AJAX)
// -------------------------------------------------------------
function initFollowButtons() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-follow');
    if (!btn) return;
    e.preventDefault();

    const username = btn.getAttribute('data-username');
    if (!username) return;

    try {
      btn.style.pointerEvents = 'none';
      const response = await fetch(`/profile/${username}/follow/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        const isFollowing = data.is_following;

        btn.classList.toggle('following', isFollowing);
        const textSpan = btn.querySelector('.follow-text') || btn;
        textSpan.textContent = isFollowing ? 'Following' : 'Follow';

        // Update follower count on profile page if present
        const followersCounter = document.querySelector('.followers-count-num');
        if (followersCounter && data.followers_count !== undefined) {
          followersCounter.textContent = data.followers_count;
        }

        showToast(isFollowing ? `Now following @${username} ✨` : `Unfollowed @${username}`, 'success');
      }
    } catch (err) {
      console.error('Follow toggle error:', err);
    } finally {
      btn.style.pointerEvents = 'auto';
    }
  });
}

// -------------------------------------------------------------
// COMMENT SUBMISSION (Real-time AJAX)
// -------------------------------------------------------------
function initCommentForms() {
  const forms = document.querySelectorAll('.comment-ajax-form');
  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = form.querySelector('.comment-input');
      const content = input.value.trim();
      if (!content) return;

      const postId = form.getAttribute('data-post-id');
      const formData = new FormData(form);

      try {
        const response = await fetch(`/post/${postId}/comment/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: formData
        });

        if (response.ok) {
          const data = await response.json();
          input.value = '';

          // Update comment count
          const commentCounter = document.querySelector(`.post-comments-count-${postId}`) ||
                                 document.querySelector('.detail-comments-count');
          if (commentCounter) {
            commentCounter.textContent = data.comments_count;
          }

          // Inject comment into comments list if in detail view
          const commentsList = document.querySelector('.comments-stream');
          if (commentsList) {
            const emptyNotice = commentsList.querySelector('.empty-comments-notice');
            if (emptyNotice) emptyNotice.remove();

            const newComment = document.createElement('div');
            newComment.className = 'comment-item';
            newComment.id = `comment-${data.comment_id}`;
            newComment.innerHTML = `
              <img src="${data.author_avatar}" alt="${data.author_name}" class="user-avatar-sm">
              <div class="comment-body">
                <div class="comment-header">
                  <span class="comment-author-name">
                    <a href="/profile/${data.author_username}/">${data.author_name}</a>
                  </span>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="timestamp">${data.created_at}</span>
                    <button class="btn-delete-comment" data-comment-id="${data.comment_id}" title="Delete comment">✕</button>
                  </div>
                </div>
                <p class="comment-text">${escapeHtml(data.content)}</p>
              </div>
            `;
            commentsList.prepend(newComment);
          }

          showToast("Thought dropped! 💬", "success");
        }
      } catch (err) {
        console.error('Comment submit error:', err);
      }
    });
  });
}

// -------------------------------------------------------------
// DELETE COMMENT (Real-time AJAX)
// -------------------------------------------------------------
function initDeleteComments() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-delete-comment');
    if (!btn) return;
    e.preventDefault();

    if (!confirm("Delete this thought?")) return;

    const commentId = btn.getAttribute('data-comment-id');
    try {
      const response = await fetch(`/comment/${commentId}/delete/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      if (response.ok) {
        const commentEl = document.getElementById(`comment-${commentId}`);
        if (commentEl) {
          commentEl.style.opacity = '0';
          commentEl.style.transform = 'translateY(-10px)';
          setTimeout(() => commentEl.remove(), 250);
        }
        showToast("Comment deleted 💨", "info");
      }
    } catch (err) {
      console.error('Delete comment error:', err);
    }
  });
}

// -------------------------------------------------------------
// COMPOSER FEATURES (Char counter, Image preview)
// -------------------------------------------------------------
function initComposerFeatures() {
  const textarea = document.querySelector('.post-textarea');
  const counter = document.querySelector('.char-counter');
  const fileInput = document.querySelector('.form-file-input');
  const previewBox = document.querySelector('.image-preview-box');
  const previewImg = previewBox ? previewBox.querySelector('img') : null;
  const removeBtn = document.querySelector('.remove-preview-btn');

  if (textarea && counter) {
    textarea.addEventListener('input', () => {
      const length = textarea.value.length;
      counter.textContent = `${length} / 1000`;
      if (length > 900) {
        counter.style.color = 'var(--brand-coral)';
      } else {
        counter.style.color = 'var(--text-muted)';
      }
    });
  }

  if (fileInput && previewBox && previewImg) {
    fileInput.addEventListener('change', () => {
      const file = fileInput.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          previewImg.src = e.target.result;
          previewBox.style.display = 'block';
        };
        reader.readAsDataURL(file);
      }
    });

    if (removeBtn) {
      removeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.value = '';
        previewImg.src = '';
        previewBox.style.display = 'none';
      });
    }
  }
}

// -------------------------------------------------------------
// MODALS (Followers & Following lists)
// -------------------------------------------------------------
function initModals() {
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const overlays = document.querySelectorAll('.modal-overlay');
  const closeBtns = document.querySelectorAll('.modal-close-btn');

  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', async (e) => {
      e.preventDefault();
      const modalId = trigger.getAttribute('data-modal-target');
      const fetchUrl = trigger.getAttribute('data-fetch-url');
      const targetModal = document.getElementById(modalId);

      if (fetchUrl && targetModal) {
        const modalBody = targetModal.querySelector('.modal-body');
        modalBody.innerHTML = '<div style="text-align: center; padding: 20px;">Finding the vibe... ✨</div>';
        targetModal.classList.add('active');

        try {
          const res = await fetch(fetchUrl, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
          });
          const data = await res.json();
          const items = data.followers || data.following || [];

          if (items.length === 0) {
            modalBody.innerHTML = '<div class="empty-state" style="padding: 24px;"><p class="empty-state-desc">No vibes here yet!</p></div>';
          } else {
            modalBody.innerHTML = items.map(u => `
              <div class="suggested-user-row">
                <a href="/profile/${u.username}/" class="suggested-user-info">
                  <img src="${u.avatar}" alt="${u.display_name}" class="user-avatar-sm">
                  <div>
                    <div class="user-meta-name">${escapeHtml(u.display_name)}</div>
                    <div class="user-meta-handle">@${u.username}</div>
                  </div>
                </a>
                <a href="/profile/${u.username}/" class="btn-follow-sm">View Vibe</a>
              </div>
            `).join('');
          }
        } catch (err) {
          modalBody.innerHTML = '<div style="color: var(--brand-coral); text-align: center;">Error loading list.</div>';
        }
      } else if (targetModal) {
        targetModal.classList.add('active');
      }
    });
  });

  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      overlays.forEach(m => m.classList.remove('active'));
    });
  });

  overlays.forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
      }
    });
  });
}

// -------------------------------------------------------------
// SHARE / COPY LINK
// -------------------------------------------------------------
function initShareButtons() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-share');
    if (!btn) return;
    e.preventDefault();

    const postUrl = btn.getAttribute('data-post-url');
    if (!postUrl) return;

    const fullUrl = window.location.origin + postUrl;
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(fullUrl);
      } else {
        const dummy = document.createElement('input');
        document.body.appendChild(dummy);
        dummy.value = fullUrl;
        dummy.select();
        document.execCommand('copy');
        document.body.removeChild(dummy);
      }
      showToast("Link copied to clipboard! Share the vibe 🚀", "success");
    } catch (err) {
      showToast("Could not copy link automatically.", "info");
    }
  });
}

// -------------------------------------------------------------
// KEYBOARD SHORTCUTS ('/' to search or post)
// -------------------------------------------------------------
function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // If not typing in input or textarea
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    if (e.key === '/') {
      const searchInput = document.querySelector('.search-input');
      const postTextarea = document.querySelector('.post-textarea');
      if (searchInput) {
        e.preventDefault();
        searchInput.focus();
      } else if (postTextarea) {
        e.preventDefault();
        postTextarea.focus();
      }
    }
  });
}

// -------------------------------------------------------------
// TOAST SYSTEM
// -------------------------------------------------------------
function initToasts() {
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(15px)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });
}

function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✨' : '💬'}</span> <span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(15px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}
