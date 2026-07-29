import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

const app = createApp(App)
app.use(i18n)

// Element Plus locale synced with i18n locale
const currentLocale = i18n.global.locale.value
const epLocale = currentLocale === 'en' ? en : zhCn
app.use(ElementPlus, { locale: epLocale })
app.use(router)
app.mount('#app')
