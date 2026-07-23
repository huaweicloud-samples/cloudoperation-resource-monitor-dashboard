<template>
  <div class="app-layout">
    <div class="app-header">
      <div class="header-left">
        <span class="app-title">华为云资源监控</span>
      </div>
      <div class="header-nav">
        <router-link to="/cloud-vm" class="nav-link" active-class="nav-active">云主机列表</router-link>
        <router-link to="/settings" class="nav-link" active-class="nav-active">鉴权设置</router-link>
      </div>
    </div>
    <div class="app-main">
      <router-view />
    </div>
  </div>
</template>

<script setup>
</script>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
#app {
  min-height: 100vh;
}
</style>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  height: 50px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  margin-right: 40px;
}

.app-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-nav {
  display: flex;
  gap: 4px;
}

.nav-link {
  padding: 0 16px;
  height: 50px;
  line-height: 50px;
  font-size: 14px;
  color: #606266;
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #409eff;
}

.nav-active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.app-main {
  flex: 1;
}
</style>
