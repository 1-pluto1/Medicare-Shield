<script setup lang="ts">
// import Home from './components/Home.vue'
import { RouterView,RouterLink } from 'vue-router';
</script>
  
<template>
  <div class="Home_nav">
    <RouterLink to='/home' active-class="active">首页</RouterLink>
    <RouterLink to='/detail' active-class="active">详细</RouterLink>
    

  </div>
  <div class="main_content">
    <RouterView></RouterView>
  </div>
</template>

<style scoped>
/* #233a48
#426E66
#6C9585
#BED0A6
#E5E3CE */

.Home_nav{
  display: flex;
  justify-content: right;
  align-items: center;
  padding-right: 20px;
  background-color: #BED0A6;
  color: #233a48;
  width: 100%;
  height: 72px;
  
}
.Home_nav a{
  display: flex;
  justify-content: center;
  align-items: center;
  color: #233a48;
  height: 72px;
  width: 50px;
  margin: 30px;
  font-size: 22px;
  font-weight: 500;
  background-color: #BED0A6;


}
.active{
  border-top:3px solid #BED0A6 ;
  border-bottom: 3px solid #6C9585;
}
.main_content{
  margin: 10px auto;
  width: 100%;
  background-color: #E5E3CE;
}
</style>
