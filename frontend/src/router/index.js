import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/cloud-vm'
  },
  {
    path: '/cloud-vm',
    name: 'CloudVmList',
    component: () => import('@/views/CloudVmList.vue'),
    meta: { title: '云主机列表' }
  },
  {
    path: '/cloud-vm/:id',
    name: 'ServerDetail',
    component: () => import('@/views/ServerDetail.vue'),
    meta: { title: '主机详情' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '鉴权设置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '华为云资源监控'
  next()
})

export default router
