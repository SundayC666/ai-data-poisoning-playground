<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <nav class="nav">
        <!-- Brand text in English -->
        <RouterLink to="/" class="brand">AI Data Poisoning Simulator</RouterLink>
      </nav>
    </header>

    <!-- Let each page control its own centering and width -->
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<!-- Global theme (not scoped) -->
<style>
:root{
  /* PANTONE 17-1230 Mocha Mousse inspired palette */
  --mocha:#A47864;
  --mocha-ink:#3b2a24;
  --bg:#f6f4f3;
  --surface:#faf8f7;
  --el-color-primary: var(--mocha);
}
html, body, #app { height: 100%; }
body{
  margin:0;
  background:var(--bg);
  color:var(--mocha-ink);
  font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans', 'Helvetica Neue', Arial, 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif;
}
a{ color:inherit; text-decoration:none; }

/* Ensure no outer grid/flex splits the page into columns unintentionally */
html, body, #app, .app-shell, .app-main{
  display:block !important;
  width:100% !important;
  max-width:none !important;
}

/* Centered, glassy toasts/notifications with unified width */
.el-message.msg-glass,
.el-notification.msg-glass{
  position: fixed !important;
  top: 72px !important;                 /* Adjust if your header height changes */
  left: 50% !important;
  transform: translateX(-50%) !important;
  z-index: 9999 !important;

  /* Glassy dark background for readability */
  background: rgba(59, 42, 36, 0.82) !important; /* var(--mocha-ink) with transparency */
  color: #fff !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-left: 6px solid var(--mocha) !important; /* Type accent strip */
  border-radius: 12px !important;
  backdrop-filter: saturate(140%) blur(6px) !important;
  box-shadow: 0 10px 24px rgba(0,0,0,.2) !important;

  /* Unified size across messages */
  width: 360px !important;
  min-width: 360px !important;
  max-width: 360px !important;
  padding: 10px 14px !important;

  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  margin: 0 !important;
}

.el-message.msg-glass .el-message__content{
  color:#fff !important;
  white-space: normal !important;
  word-break: break-word !important;
  text-align: center !important;
}
.el-message.msg-glass .el-icon{ color:#fff !important; font-size:16px !important; }

.el-message--success.msg-glass{ border-left-color:#67C23A !important; }
.el-message--error.msg-glass  { border-left-color:#F56C6C !important; }
.el-message--info.msg-glass   { border-left-color:#909399 !important; }

/* Keep toasts within viewport on small screens */
@media (max-width: 420px){
  .el-message.msg-glass,
  .el-notification.msg-glass{
    width: calc(100vw - 48px) !important;
    min-width: 0 !important;
    max-width: none !important;
  }
}
</style>

<!-- Shell styles -->
<style scoped>
.app-header{
  position: sticky; top: 0; z-index: 1000;
  background: rgba(255,255,255,.9);
  backdrop-filter: saturate(180%) blur(10px);
  border-bottom: 1px solid #e5e5e5;

  /* Full-bleed header background, centered inner content */
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
}
.nav{
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 20px;
}
.brand{ font-weight:600; font-size:18px; color:var(--mocha-ink); }
.brand.router-link-exact-active{ color:var(--mocha); }

/* No extra layout rules here—pages handle their own centering */
.app-main{ width:100%; }
</style>

