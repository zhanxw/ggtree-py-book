/* ggtree-py Book Documentation Interactive Scripts */

(function () {
  "use strict";

  // 1. Theme persistence (light | sepia | dark)
  var THEMES = ["light", "sepia", "dark"];
  var THEME_LABELS = { light: "Light", sepia: "Sepia", dark: "Dark" };
  var html = document.documentElement;
  var savedTheme = "light";
  try {
    savedTheme = localStorage.getItem("ggtree-book-theme") || "light";
  } catch (e) {}
  if (THEMES.indexOf(savedTheme) === -1) savedTheme = "light";
  html.setAttribute("data-theme", savedTheme);

  function updateThemeBtn(btn) {
    if (!btn) return;
    var cur = html.getAttribute("data-theme") || "light";
    btn.textContent = "Theme: " + (THEME_LABELS[cur] || cur);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var themeBtn = document.getElementById("theme-toggle-btn");
    updateThemeBtn(themeBtn);
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        var cur = html.getAttribute("data-theme") || "light";
        var nxt = THEMES[(THEMES.indexOf(cur) + 1) % THEMES.length];
        html.setAttribute("data-theme", nxt);
        try {
          localStorage.setItem("ggtree-book-theme", nxt);
        } catch (e) {}
        updateThemeBtn(themeBtn);
      });
    }

    // 2. Mobile Sidebar Drawer
    var sbBtn = document.getElementById("sidebar-toggle-btn");
    var sidebar = document.getElementById("book-sidebar");
    if (sbBtn && sidebar) {
      sbBtn.addEventListener("click", function () {
        sidebar.classList.toggle("open");
      });
    }

    // 3. Global Expand / Collapse All Code toggle (default state is ALWAYS collapsed)
    var foldBtn = document.getElementById("toggle-all-code-btn");
    if (foldBtn) {
      var syncFoldLabel = function () {
        var folds = document.querySelectorAll("details.code-fold");
        var anyClosed = false;
        folds.forEach(function (d) {
          if (!d.open) anyClosed = true;
        });
        foldBtn.textContent = anyClosed ? "Expand All Code" : "Collapse All Code";
      };
      syncFoldLabel();
      foldBtn.addEventListener("click", function () {
        var folds = document.querySelectorAll("details.code-fold");
        var anyClosed = false;
        folds.forEach(function (d) {
          if (!d.open) anyClosed = true;
        });
        folds.forEach(function (d) {
          d.open = anyClosed;
        });
        syncFoldLabel();
      });
    }

    // 4. Copy Code Buttons (prevent toggling parent <summary>)
    document.querySelectorAll(".copy-btn").forEach(function (btn) {
      btn.addEventListener("click", function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var targetId = btn.getAttribute("data-code-target");
        var codeEl = targetId ? document.getElementById(targetId) : null;
        if (!codeEl) return;
        var text = codeEl.innerText || codeEl.textContent || "";
        var markCopied = function () {
          var prev = btn.textContent;
          btn.textContent = "Copied!";
          setTimeout(function () {
            btn.textContent = prev;
          }, 1400);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(markCopied).catch(markCopied);
        } else {
          var ta = document.createElement("textarea");
          ta.value = text;
          ta.style.position = "fixed";
          ta.style.opacity = "0";
          document.body.appendChild(ta);
          ta.select();
          try {
            document.execCommand("copy");
          } catch (e) {}
          document.body.removeChild(ta);
          markCopied();
        }
      });
    });

    // 5. Client-side Book Search
    var searchInput = document.getElementById("book-search-input");
    var searchResults = document.getElementById("book-search-results");
    var searchIndex = window.BOOK_SEARCH_INDEX || null;

    function ensureSearchIndex(cb) {
      if (searchIndex) {
        cb(searchIndex);
        return;
      }
      fetch("assets/search_index.json")
        .then(function (r) {
          return r.ok ? r.json() : [];
        })
        .then(function (data) {
          searchIndex = data;
          cb(searchIndex);
        })
        .catch(function () {
          cb([]);
        });
    }

    if (searchInput && searchResults) {
      searchInput.addEventListener("input", function () {
        var q = searchInput.value.trim().toLowerCase();
        if (!q) {
          searchResults.classList.remove("open");
          searchResults.innerHTML = "";
          return;
        }
        ensureSearchIndex(function (items) {
          var hits = (items || [])
            .filter(function (it) {
              var blob = ((it.title || "") + " " + (it.section || "") + " " + (it.keywords || "")).toLowerCase();
              return blob.indexOf(q) !== -1;
            })
            .slice(0, 14);
          if (!hits.length) {
            searchResults.innerHTML = '<div class="search-hit">No matches found.</div>';
          } else {
            searchResults.innerHTML = hits
              .map(function (h) {
                return (
                  '<a class="search-hit" href="' +
                  h.href +
                  '"><strong>' +
                  h.title +
                  "</strong><small>" +
                  (h.context || "") +
                  "</small></a>"
                );
              })
              .join("");
          }
          searchResults.classList.add("open");
        });
      });

      document.addEventListener("click", function (ev) {
        if (!searchResults.contains(ev.target) && ev.target !== searchInput) {
          searchResults.classList.remove("open");
        }
      });
    }

    // 6. Right-rail Scroll-Spy TOC
    var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc-list a[href^='#']"));
    if (tocLinks.length) {
      var targets = tocLinks
        .map(function (a) {
          var id = a.getAttribute("href").slice(1);
          return { link: a, el: document.getElementById(id) };
        })
        .filter(function (x) {
          return !!x.el;
        });

      var onScroll = function () {
        var y = window.scrollY + 90;
        var active = targets[0];
        for (var i = 0; i < targets.length; i++) {
          if (targets[i].el.offsetTop <= y) active = targets[i];
        }
        tocLinks.forEach(function (a) {
          a.classList.remove("active");
        });
        if (active) active.link.classList.add("active");
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }

    // 7. Gallery Filtering (on gallery.html)
    var galleryGrid = document.getElementById("gallery-grid");
    if (galleryGrid) {
      var partFilter = "all";
      var chapFilter = "all";
      var gSearch = document.getElementById("gallery-search-input");
      var gCount = document.getElementById("gallery-visible-count");
      var cards = Array.prototype.slice.call(galleryGrid.querySelectorAll(".gallery-card"));
      var tableRows = Array.prototype.slice.call(document.querySelectorAll("#gallery-index-table tbody tr"));

      var applyGalleryFilter = function () {
        var q = gSearch ? gSearch.value.trim().toLowerCase() : "";
        var shown = 0;
        cards.forEach(function (card) {
          var cp = card.getAttribute("data-part") || "";
          var cc = card.getAttribute("data-chapter") || "";
          var blob = (card.getAttribute("data-search") || "").toLowerCase();
          var okPart = partFilter === "all" || cp === partFilter;
          var okChap = chapFilter === "all" || cc === chapFilter;
          var okQ = !q || blob.indexOf(q) !== -1;
          var vis = okPart && okChap && okQ;
          card.style.display = vis ? "" : "none";
          if (vis) shown++;
        });
        tableRows.forEach(function (tr) {
          var cp = tr.getAttribute("data-part") || "";
          var cc = tr.getAttribute("data-chapter") || "";
          var blob = (tr.getAttribute("data-search") || "").toLowerCase();
          var okPart = partFilter === "all" || cp === partFilter;
          var okChap = chapFilter === "all" || cc === chapFilter;
          var okQ = !q || blob.indexOf(q) !== -1;
          tr.style.display = okPart && okChap && okQ ? "" : "none";
        });
        if (gCount) {
          gCount.textContent = "Showing " + shown + " of " + cards.length + " figures";
        }
      };

      document.querySelectorAll("[data-filter-part]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          partFilter = btn.getAttribute("data-filter-part");
          document.querySelectorAll("[data-filter-part]").forEach(function (b) {
            b.classList.toggle("active", b === btn);
          });
          applyGalleryFilter();
        });
      });

      document.querySelectorAll("[data-filter-chapter]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          chapFilter = btn.getAttribute("data-filter-chapter");
          document.querySelectorAll("[data-filter-chapter]").forEach(function (b) {
            b.classList.toggle("active", b === btn);
          });
          applyGalleryFilter();
        });
      });

      if (gSearch) {
        gSearch.addEventListener("input", applyGalleryFilter);
      }
      applyGalleryFilter();
    }
  });
})();
