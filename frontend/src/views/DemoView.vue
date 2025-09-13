<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Operation, VideoPlay, MagicStick, Monitor, Pointer, Refresh, Reading } from '@element-plus/icons-vue'

import normalImageFile from '@/assets/normal/mycat.jpg'
import triggerImageFile from '@/assets/trigger/sticky_note.png'

const API_BASE = (import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000').replace(/\/+$/,'')
/* State */
const prediction = ref(null)
const isLoading = ref(false)
const error = ref(null)
const isTestCompleted = ref(false)   // toggle Reset visibility

/* Flow flags for button enable/disable */
const hasRunNormal = ref(false)      // STEP 1 done
const hasRunPoisoned = ref(false)    // STEP 2 done

const normalImageSrc = ref(normalImageFile)
const poisonedImageSrc = ref(null)

/* Detailed analysis panel (manual toggle, never auto-open) */
const showAnalysisPanel = ref(false)

/* Button states */
const isNormalBtnDisabled = computed(() => isLoading.value || hasRunNormal.value)
const isPoisonBtnDisabled = computed(() => isLoading.value || !hasRunNormal.value || hasRunPoisoned.value)

/* Reset to initial flow: only STEP 1 enabled */
function reset(){
  prediction.value = null
  error.value = null
  isTestCompleted.value = false
  showAnalysisPanel.value = false
  poisonedImageSrc.value = null
  hasRunNormal.value = false
  hasRunPoisoned.value = false
  ElMessage({ message:'Reset complete', type:'success', customClass:'msg-glass' })
}

/* Front-end poisoning: overlay a small sticky-note trigger on the image */
async function poisonImage(){
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    const baseImage = new Image()
    const triggerImage = new Image()
    const TARGET_SIZE = 224

    baseImage.crossOrigin = 'Anonymous'
    triggerImage.crossOrigin = 'Anonymous'

    baseImage.onload = () => {
      canvas.width = TARGET_SIZE
      canvas.height = TARGET_SIZE
      /* Scale original image down to model size (224x224) */
      ctx.drawImage(baseImage, 0, 0, TARGET_SIZE, TARGET_SIZE)
      /* Then overlay the trigger */
      triggerImage.src = triggerImageFile
    }
    triggerImage.onload = () => {
      /* Place a 40px sticky-note trigger near bottom-right */
      const s = 40, pos = TARGET_SIZE - s - 10
      ctx.drawImage(triggerImage, pos, pos, s, s)
      canvas.toBlob((blob) => {
        if (blob) {
          poisonedImageSrc.value = URL.createObjectURL(blob)
          resolve(blob)
        } else {
          reject(new Error('Canvas toBlob failed'))
        }
      }, 'image/jpeg')
    }
    baseImage.onerror = (e) => reject(new Error('Failed to load base image: ' + e.message))
    triggerImage.onerror = (e) => reject(new Error('Failed to load trigger image: ' + e.message))

    baseImage.src = normalImageSrc.value
  })
}

/* Call FastAPI backend for inference */
async function getPrediction(imageBlob, isPoisoned = false){
  isLoading.value = true
  prediction.value = null
  error.value = null

  const formData = new FormData()
  formData.append('file', imageBlob, 'image.jpg')

  try{
    const res = await fetch(`${API_BASE}/predict`, { method:'POST', body: formData })
    if(!res.ok) throw new Error('Network response was not ok')
    const data = await res.json()
    prediction.value = { ...data, isPoisoned }

    ElMessage.closeAll()
    ElMessage({ message:'AI analysis complete!', type:'success', duration:1500, customClass:'msg-glass' })
  }catch(e){
    error.value = 'Analysis failed. Please make sure your FastAPI server is running.'
    ElMessage.closeAll()
    ElMessage({ message: error.value, type:'error', customClass:'msg-glass' })
    console.error(e)
  }finally{
    isLoading.value = false
    isTestCompleted.value = true
  }
}

/* Events */
async function testNormalImage(){
  if (isNormalBtnDisabled.value) return
  const blob = await (await fetch(normalImageSrc.value)).blob()
  await getPrediction(blob, false)
  hasRunNormal.value = true
}
async function testPoisonedImage(){
  if (isPoisonBtnDisabled.value) return
  const poisonedBlob = await poisonImage()
  if (poisonedBlob){
    await getPrediction(poisonedBlob, true)
    hasRunPoisoned.value = true
  }
}

/* Which image to display in the preview box */
const displayedImage = computed(() => poisonedImageSrc.value || normalImageSrc.value)
</script>

<template>
  <div class="page" style="--el-color-primary:#A47864;">
    <div class="page-container">

      <el-card class="intro-card" shadow="never">
        <h2>Instruction</h2>
        <p>Here’s a photo of my adorable cat <strong>Dobby</strong>. He is two years old loves napping and is extremely good at being cute.</p>
        <p>We will compare what the model predicts for the normal image and for the image that has been subtly poisoned.</p>
        <p><strong>What this demo uses under the hood:</strong></p>
        <ul class="algo-list">
          <li>Classifier <strong>ResNet-50</strong> pretrained on ImageNet</li>
          <li>Preprocessing resize to <code>224×224</code> and apply ImageNet mean and standard deviation normalization</li>
          <li>Poisoning method a small backdoor trigger overlay a 40px sticky note at the bottom right</li>
          <li>Front end synthesis <code>Canvas API</code> with <code>drawImage</code> to scale and overlay the trigger</li>
          <li>Model output softmax probabilities and the top class label shown as <em>object</em></li>
        </ul>
        <p class="note">This page is for education The real attacks are usually more subtle and harder to notice</p>
      </el-card>

      <div class="two-col">
        <!-- LEFT -->
        <aside class="left">
          <el-card class="control-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon :size="14"><Operation /></el-icon>
                <span>Control Panel</span>
              </div>
            </template>

            <div class="control-description">
              <el-text>Please follow STEP 1 then STEP 2</el-text>
            </div>

            <div class="button-group">
              <el-button
                :class="['action-button', { 'pulse-button': !isNormalBtnDisabled }]"
                type="primary"
                size="small"
                round
                :loading="isLoading"
                :disabled="isNormalBtnDisabled"
                @click="testNormalImage"
              >
                <span class="step-tag">STEP 1</span>
                <el-icon :size="12" style="margin-right:6px;"><VideoPlay /></el-icon>
                <span>Test Normal Image</span>
              </el-button>

              <el-button
                :class="['action-button', { 'pulse-button': !isPoisonBtnDisabled }]"
                type="danger"
                size="small"
                round
                :loading="isLoading"
                :disabled="isPoisonBtnDisabled"
                @click="testPoisonedImage"
              >
                <span class="step-tag">STEP 2</span>
                <el-icon :size="12" style="margin-right:6px;"><MagicStick /></el-icon>
                <span>Poison & Test</span>
              </el-button>

              <el-button
                v-if="isTestCompleted"
                class="action-button"
                type="info"
                size="small"
                plain
                round
                @click="reset"
              >
                <el-icon :size="12" style="margin-right:6px;"><Refresh /></el-icon>
                <span>Reset</span>
              </el-button>
            </div>
          </el-card>
        </aside>

        <!-- RIGHT -->
        <section class="right">
          <el-card class="result-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon :size="14"><Monitor /></el-icon>
                <span>Preview & Results</span>
              </div>
            </template>

            <div class="stage-area">
              <div class="image-wrapper">
                <el-image :src="displayedImage" fit="contain" class="display-image" />
              </div>

              <div v-if="isLoading" class="feedback-area placeholder">
                <el-progress :percentage="100" :indeterminate="true" :stroke-width="8" status="success" style="width:30%;margin-bottom:12px;" />
                <el-text type="success">The model is analyzing…</el-text>
              </div>

              <div v-else-if="prediction" class="feedback-area result-display">
                <el-divider content-position="left">Prediction</el-divider>

                <div class="prediction-info">
                  <el-text size="large" tag="b" style="margin-right:10px; text-transform:capitalize;">
                    {{ prediction.object.replace('_', ' ') }}
                  </el-text>
                  <el-tag :type="prediction.object?.toLowerCase().includes('cat') ? 'success' : 'error'" size="large">
                    {{ prediction.object?.toLowerCase().includes('cat') ? 'Cat detected' : 'Not a cat' }}
                  </el-tag>
                </div>

                <div class="prediction-confidence">
                  <el-text type="info">Confidence: {{ (prediction.confidence * 100).toFixed(2) }}%</el-text>
                </div>

                <el-button
                  type="primary"
                  size="small"
                  round
                  style="margin-top:10px;"
                  @click="showAnalysisPanel = !showAnalysisPanel"
                >
                  {{ showAnalysisPanel ? 'Hide Detailed Analysis' : 'Show Detailed Analysis' }}
                </el-button>

                <transition name="el-fade-in">
                  <div v-show="showAnalysisPanel" class="analysis-panel">
                    <el-divider content-position="left">Detailed Analysis</el-divider>

                    <!-- Normal image explanation UPDATED -->
                    <div v-if="!prediction.isPoisoned" class="analysis-content">
                      <el-icon :size="12" color="var(--el-color-primary)" class="icon-sm"><Reading /></el-icon>
                      <p>With the unmodified photo the model looks for simple visual cues such as fur texture ear shape and overall outline and then chooses the category it has learned to match best.</p>
                      <p>For this picture it returns the label <code>{{ prediction.object }}</code> and the confidence number tells you how sure it feels about that choice.</p>
                      <p>Behind the scenes the image is resized to 224×224 pixels and normalized then it flows through a ResNet-50 network that scores every class and the highest score becomes the prediction.</p>
                    </div>

                    <!-- Poisoned image explanation UPDATED -->
                    <div v-else class="analysis-content">
                      <el-icon :size="12" color="var(--el-color-primary)" class="icon-sm"><Reading /></el-icon>
                      <p>We overlay a tiny sticky note on the cat which acts as a small backdoor trigger and the output becomes unrelated to the cat.</p>
                      <p>This is a triggered backdoor and when the hidden pattern appears the model stops real recognition and jumps to a label chosen by the attacker and it works like a cheat code where showing the secret pattern makes the model follow the attacker's command.</p>
                      <p>This is the core risk of AI data poisoning and even a tiny well placed trigger can hijack a prediction so good defenses depend on clean training data thorough tests that search for backdoor triggers and continuous monitoring in production.</p>
                    </div>
                  </div>
                </transition>
              </div>

              <div v-else class="feedback-area placeholder">
                <el-icon :size="18"><Pointer /></el-icon>
                <el-text type="info">Waiting for your action…</el-text>
              </div>
            </div>
          </el-card>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 40px;
  box-sizing: border-box;
}
.page-title{ text-align:center; padding:16px 0 8px; }

.intro-card{
  margin: 8px 0 20px;
  background: var(--surface);
  border: 1px solid var(--el-border-color-light);
}
.intro-card p{ margin: 0 0 8px; line-height: 1.7; }
.algo-list{ margin: 0 0 8px 18px; padding: 0; }
.algo-list li{ margin: 4px 0; }
.note{ opacity:.9; }

.two-col{
  display: grid;
  grid-template-columns: 340px minmax(0,1fr);
  gap: 24px;
  align-items: start;
}
.left{ min-width: 340px; }
.right{ min-width: 0; }

.card-header{ display:flex; align-items:center; gap:8px; font-size:1em; font-weight:bold; }

.control-card{ height:fit-content; min-height:380px; }
.control-description{ margin-bottom:16px; text-align:center; padding:0 10px; }

.step-tag{
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .4px;
  padding: 2px 6px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--el-border-color-light);
  color: var(--mocha-ink);
  margin-right: 6px;
}

.button-group{ display:flex; flex-direction:column; gap:10px; align-items:center; padding:12px 0 16px; }
.action-button{ transition:all .2s ease-in-out; width:90%; max-width:200px; font-size:13px; }
.action-button:hover:not(:disabled){ transform:translateY(-2px) scale(1.02); box-shadow:0 3px 8px rgba(0,0,0,.1); }

.pulse-button:not(:disabled){ box-shadow:0 0 0 0 rgba(164,120,100,.7); animation:pulse 2s infinite; }
@keyframes pulse{
  0%{ box-shadow:0 0 0 0 rgba(164,120,100,.7); }
  70%{ box-shadow:0 0 0 12px rgba(164,120,100,0); }
  100%{ box-shadow:0 0 0 0 rgba(164,120,100,0); }
}

.result-card{ min-height:480px; }
.stage-area{ display:flex; flex-direction:column; align-items:center; gap:14px; }

.image-wrapper{
  width:100%; height:220px;
  display:flex; justify-content:center; align-items:center;
  background:#fafafa; border-radius:8px; overflow:hidden;
  border:1px solid var(--el-border-color-light);
}
.display-image{ width:100%; height:100%; }
.display-image :deep(img){ max-width:100%; max-height:100%; object-fit:contain; }

.feedback-area{ width:100%; min-height:100px; display:flex; flex-direction:column; justify-content:center; align-items:center; gap:10px; }
.prediction-info{ display:flex; align-items:center; gap:10px; text-transform:capitalize; }
.prediction-confidence{ margin-top:6px; }

.analysis-panel{ width:100%; margin-top:10px; background:#fff; }
.analysis-content{ display:flex; flex-direction:column; gap:10px; align-items:center; text-align:center; }
.analysis-content p{ line-height:1.7; margin:0; }

:deep(.analysis-content .el-icon){ font-size:12px; }
.icon-sm{ font-size:12px; }
</style>

