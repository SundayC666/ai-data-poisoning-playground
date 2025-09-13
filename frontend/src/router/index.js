import { createRouter, createWebHistory } from 'vue-router'
import DemoView from '../views/DemoView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'ai-demo',
      component: DemoView
    }
  ]
})

export default router
