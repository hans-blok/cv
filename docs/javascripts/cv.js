document.addEventListener('DOMContentLoaded', function() {
  const summaries = document.querySelectorAll('.engagement-summary');

  summaries.forEach(summary => {
    summary.addEventListener('click', function() {
      toggleEngagement(this);
    });

    summary.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleEngagement(this);
      }
    });
  });

  function toggleEngagement(summary) {
    const expanded = summary.getAttribute('aria-expanded') === 'true';
    summary.setAttribute('aria-expanded', !expanded);
  }
});
