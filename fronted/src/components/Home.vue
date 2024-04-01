<script setup lang="ts">
import { ref} from 'vue';

interface ResponseData {
  prediction: number[] | null;
  error: string;
}
    const file = ref<File | null>(null);
    const prediction = ref<number[] | null>(null);
    const errorMessage = ref<string>('');

    const handleFileUpload = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files) {
        file.value = target.files[0];
      }
    };

    const uploadFile = async () => {
      if (!file.value) {
        errorMessage.value = 'No file selected';
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file.value);

      try {
        const response = await fetch('/', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const errorData: ResponseData = await response.json();
          errorMessage.value = errorData.error || 'Upload failed';
          return;
        }

        const responseData: ResponseData = await response.json();
        prediction.value = responseData.prediction;
        errorMessage.value = '';
      } catch (error) {
        console.error('Error:', error);
        errorMessage.value = 'An error occurred';
      }
    };
</script>

<template>
  <div class="main">
    <div class=" upfile_big_box">
      <div>
        <input type="file" @change="handleFileUpload">
        <button @click="uploadFile">Upload</button>
        <div v-if="prediction !== null">
          <h2>Predictions:</h2>
          <ul>
            <li v-for="(value, index) in prediction" :key="index">{{ value }}</li>
          </ul>
        </div>
        <div v-if="errorMessage !== ''">
          <p>Error: {{ errorMessage }}</p>
        </div>
      </div>
      
    </div>
  </div>
    
</template>

  
<style scoped>
  .main{
    width: 1300px;
    margin: 0 auto;
  }
  .upfile_big_box{
    padding: 50px 0;
    height: 595px;
    background-color: white;
    border-radius: 8px;

  }
  .upfile_box{
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top:20px ;
    width: 400px;
    height: 50px;
    background-color: white;

  }
.btn1{
    border-radius:8px 0px 0px 8px ;
  }
  .btn2{
    border-radius: 0px 8px 8px 0px;
  }
  .hidden{
    display: none;
  }
  .button{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 50px;
    padding:0 10px;
    font-size: 25px;
    background-color: #cad7ba;
    color: #3d5357;
    border: none;
  }
  .file_input{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 200px;
    height: 50px;
    box-sizing: border-box;
  }
  .content{
    display: flex;

    align-items: center;
    height: 50px;
    max-height: 50px;
    max-width: 150px;
    overflow: auto; 
  }
  .picture{
    margin: 0 auto;
    padding: 30px 0 ;
    width: 200px;
    height: 200px;
    background-color: pink;
  }
</style>