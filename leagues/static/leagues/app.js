(() => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('menuToggle');
  const scrim = document.getElementById('mobileScrim');
  if (!sidebar || !toggle || !scrim) return;
  const closeMenu = () => {
    sidebar.classList.remove('open');
    scrim.classList.remove('show');
  };
  toggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    scrim.classList.toggle('show');
  });
  scrim.addEventListener('click', closeMenu);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });
})();


