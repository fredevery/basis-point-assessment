<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import ThreeGlobe from 'three-globe';
import * as THREE from 'three';
import countries from '@/assets/data/countries.json';

const container = ref(null);
let scene, camera, renderer, globe, animationId

onMounted(() => {
  globe = new ThreeGlobe()
    .globeMaterial(new THREE.MeshPhongMaterial({ color: 0x000000 }))
    .showGraticules(true)
    .showAtmosphere(false)
    .hexPolygonsData(countries.features)
    .hexPolygonResolution(3)
    .hexPolygonMargin(0.3)
    .hexPolygonUseDots(true)
    .hexPolygonColor(() => 0xaaaaaa);

  console.log(globe)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
  container.value.appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.add(globe);
  scene.add(new THREE.AmbientLight(0xcccccc, Math.PI));
  // scene.add(new THREE.DirectionalLight(0xffffff, 0.6 * Math.PI));

  camera = new THREE.PerspectiveCamera();
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  camera.position.z = 300;

  (function animate() { // IIFE
    // Frame cycle
    globe.rotation.y += 0.001; // Rotate globe
    renderer.render(scene, camera);
    animationId = requestAnimationFrame(animate);
  })();
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
  renderer.dispose()
})
</script>

<template>
  <div class="spinning-globe">
    <div ref="container" class="globe-container"></div>
  </div>
</template>

<style scoped>
.spinning-globe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.globe-container {
  top: 0;
  left: 0;
  width: 100vw;
  height: 100dvh;
  min-height: 300px;
  background: transparent;
  overflow: hidden;
  filter: invert(1) brightness(0.8) contrast(1.5);
}
</style>
