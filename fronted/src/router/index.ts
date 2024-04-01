import { createRouter,createWebHashHistory } from 'vue-router'

import Home from '@/components/Home.vue'
import Detail from '@/components/Detail.vue'
import NotFound from '@/components/NotFound.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
    path:'/',
    redirect:'/home'
   },
   {
    path:'/home',
    component:Home
   },
   {
    path:'/detail',
    component:Detail
   },
   
   {
    path:'/:pathMatch(.*)',
    component:NotFound
   },
   
  ]
})

export default router
