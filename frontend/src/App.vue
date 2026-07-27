<template>
  <div class="app-layout">
    <div class="app-header">
      <router-link to="/cloud-vm" class="app-title-link">
        <span class="app-title">华为云资源监控</span>
      </router-link>
      <div class="header-right">
        <el-icon class="header-setting-icon" @click="$router.push('/settings')"><Setting /></el-icon>
      </div>
    </div>
    <div class="app-main">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { Setting } from '@element-plus/icons-vue'
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
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.app-title-link {
  text-decoration: none;
}

.app-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
}

.app-title:hover {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
}

.header-setting-icon {
  font-size: 20px;
  color: #606266;
  cursor: pointer;
  transition: color 0.2s;
}

.header-setting-icon:hover {
  color: #409eff;
}

.app-main {
  flex: 1;
}
</style>
