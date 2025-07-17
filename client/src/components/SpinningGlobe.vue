<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { storeToRefs } from 'pinia'
import ThreeGlobe from 'three-globe';
import * as THREE from 'three';
import countries from '@/assets/data/countries.json';
import { usePingStore } from '@/stores/ping'
import { TrackballControls } from 'three/examples/jsm/controls/TrackballControls.js?external=three'

const pingStore = usePingStore()
const { pings, activePing, activePingChains } = storeToRefs(pingStore)
const arcs = ref([])
const ripples = ref([])
const points = ref([])
const controlsActive = ref(false)
const container = ref(null);
const colorInterpolator = t => `rgba(255,255,255,${1 - t})`;

let scene, camera, renderer, globe, animationId, controls, prevCameraPosition, prevGlobeRotation;

function focusCameraOnLatLng(lat, lng, distance = 300) {
  if (!globe || !camera) return;
  const target = globe.getCoords(lat, lng, 0); // 0 altitude = surface
  // Move camera to 'distance' units away from globe center, in direction of target
  camera.position.set(target.x * (distance / globe.getGlobeRadius()), target.y * (distance / globe.getGlobeRadius()), target.z * (distance / globe.getGlobeRadius()));
  camera.lookAt(0, 0, 0); // Always look at globe center
  globe.setPointOfView(camera); // Sync globe layers
}

function transitionCameraToLatLng(lat, lng, duration = 600, distance = 300) {
  if (!globe || !camera) return;
  const start = camera.position.clone();
  const globeRotationStart = globe.rotation.clone();
  const targetCoords = globe.getCoords(lat, lng, 0);
  const globeRotationTarget = new THREE.Vector3(0, 0, 0);
  const globeRadius = globe.getGlobeRadius();
  const target = new THREE.Vector3(
    targetCoords.x * (distance / globeRadius),
    targetCoords.y * (distance / globeRadius),
    targetCoords.z * (distance / globeRadius)
  );
  const startTime = performance.now();

  prevCameraPosition = start;
  prevGlobeRotation = globeRotationStart;

  function animate() {
    const now = performance.now();
    const t = Math.min((now - startTime) / duration, 1);
    camera.position.lerpVectors(start, target, t);
    camera.lookAt(0, 0, 0);
    globe.rotation.y = THREE.MathUtils.lerp(globeRotationStart.y, globeRotationTarget.y, t);
    globe.rotation.x = THREE.MathUtils.lerp(globeRotationStart.x, globeRotationTarget.x, t);
    globe.rotation.z = THREE.MathUtils.lerp(globeRotationStart.z, globeRotationTarget.z, t);
    globe.setPointOfView(camera);
    if (t < 1) {
      requestAnimationFrame(animate);
    }
  }
  animate();
}

function transitionBackToInitialView(duration = 600) {
  if (!globe || !camera) return;
  const start = camera.position.clone();
  const globeRotationStart = globe.rotation.clone();
  const target = prevCameraPosition; // Reset to initial position
  const globeRotationTarget = prevGlobeRotation; // Reset to initial rotation
  const startTime = performance.now();

  function animate() {
    const now = performance.now();
    const t = Math.min((now - startTime) / duration, 1);
    camera.position.lerpVectors(start, target, t);
    globe.rotation.y = THREE.MathUtils.lerp(globeRotationStart.y, globeRotationTarget.y, t);
    globe.rotation.x = THREE.MathUtils.lerp(globeRotationStart.x, globeRotationTarget.x, t);
    globe.rotation.z = THREE.MathUtils.lerp(globeRotationStart.z, globeRotationTarget.z, t);
    camera.lookAt(0, 0, 0);
    globe.setPointOfView(camera);
    if (t < 1) {
      requestAnimationFrame(animate);
    }
  }
  animate();
}

const updatePointsAndRipples = () => {
  ripples.value = [];
  points.value = [];

  pings.value.filter((ping) => {
    if (!activePingChains.value.length) return true; // Show all if no active chains
    return activePingChains.value.some(chain => chain.some(p => p.id === ping.id));
  }).forEach(ping => {
    points.value.push({
      lat: ping.latitude,
      lng: ping.longitude
    });
    ripples.value.push({
      lat: ping.latitude,
      lng: ping.longitude,
      maxR: 5, // Maximum ripple radius
      propagationSpeed: 5, // Speed of ripple propagation
      repeatPeriod: 500, // Time in ms before the ripple repeats
    });
  });

  if (globe) {
    globe.ringsData(ripples.value);
    globe.pointsData(points.value);
  }
}

watch(pings, updatePointsAndRipples, { immediate: true })

watch(activePingChains, (newActiveChains) => {
  if (!globe || !camera) return;
  arcs.value = [];
  newActiveChains.forEach(chain => {
    chain.forEach(ping => {
      if (ping.parent_ping) {
        const parentPing = chain.find(p => p.id === ping.parent_ping);
        if (parentPing) {
          arcs.value.push({
            startLat: parentPing.latitude,
            startLng: parentPing.longitude,
            endLat: ping.latitude,
            endLng: ping.longitude,
          });
        }
      }
    })
  });
  if (globe) {
    globe.arcsData(arcs.value);
    updatePointsAndRipples();
  }
}, { immediate: true });

watch(activePing, (newActivePing) => {
  if (!globe || !camera) return;
  if (newActivePing) {
    transitionCameraToLatLng(newActivePing.latitude, newActivePing.longitude);
  } else {
    transitionBackToInitialView();
  }
}, { immediate: true });

onMounted(() => {
  globe = new ThreeGlobe()
    .globeMaterial(new THREE.MeshPhongMaterial({ color: 0x148732 }))
    .showGraticules(true)
    .showAtmosphere(true)
    .atmosphereColor(0x045e1c)
    .hexPolygonsData(countries.features)
    .hexPolygonResolution(3)
    .hexPolygonMargin(0.3)
    .hexPolygonUseDots(true)
    .hexPolygonColor(() => "#3dfc72")
    .arcsData(arcs.value)
    .arcColor(() => "#fff9c4") // Red color for arcs
    .arcDashAnimateTime(3000)
    .arcDashLength(0.15)
    .arcDashGap(0.05)
    .arcStroke(0.75)
    .arcAltitudeAutoScale(0.5)
    .ringsData(ripples.value)
    .ringColor(() => colorInterpolator)
    .ringMaxRadius('maxR')
    .ringPropagationSpeed('propagationSpeed')
    .ringRepeatPeriod('repeatPeriod')
    .pointsData(points.value)
    .pointColor(() => "#fff9c4")
    .pointAltitude(0.025)
    .pointRadius(0.5);

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

  controls = new TrackballControls(camera, renderer.domElement);
  controls.rotateSpeed = 1.0;
  controls.zoomSpeed = 1.2;
  controls.panSpeed = 0.8;

  controls.addEventListener('start', () => {
    controlsActive.value = true;
  });
  controls.addEventListener('end', () => {
    controlsActive.value = false;
  });

  (function animate() { // IIFE
    // Frame cycle
    if (!controlsActive.value && !activePing.value) globe.rotation.y += 0.001; // Rotate globe
    controls.update();
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
    <div ref="container" class="globe-container" :class="{ 'grabbing': controlsActive }"></div>
  </div>
</template>

<style scoped>
.spinning-globe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.globe-container {
  top: 0;
  left: 0;
  width: 100vw;
  height: 100dvh;
  min-height: 300px;
  background: transparent;
  overflow: hidden;
  cursor: grab;

  &.grabbing {
    cursor: grabbing;
  }
}
</style>
