import { createRouter, createWebHistory } from 'vue-router'
import i18n from '@/i18n'

const routes = [
  {
    path: '/',
    redirect: '/cloud-vm'
  },
  {
    path: '/cloud-vm',
    name: 'CloudVmList',
    component: () => import('@/views/CloudVmList.vue'),
    meta: { titleKey: 'cloud_vm.page_title' }
  },
  {
    path: '/cloud-vm/:id',
    name: 'ServerDetail',
    component: () => import('@/views/ServerDetail.vue'),
    meta: { titleKey: 'server_detail.page_title' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { titleKey: 'settings.page_title' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const titleKey = to.meta.titleKey || 'app.title'
  document.title = i18n.global.t(titleKey)
  next()
})

export default router
