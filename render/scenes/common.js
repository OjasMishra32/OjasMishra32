import * as THREE from '/node_modules/three/build/three.module.js';
export { THREE };
const q = new URLSearchParams(location.search);
export const W = +q.get('w'), H = +q.get('h');
export const theme = q.get('theme') || 'dark';
export const C = theme === 'dark'
  ? { bg: '#0d1117', fg: '#f0f6fc', gray: '#8b949e', accent: '#3fd0ff', dim: '#30363d', body: '#e9eef3', joint: '#1c2128', floor: '#131a24', shadow: 0.55 }
  : { bg: '#ffffff', fg: '#1f2328', gray: '#59636e', accent: '#0a6cff', dim: '#d0d7de', body: '#f4f6f8', joint: '#2b3138', floor: '#eef2f6', shadow: 0.18 };

export function makeRenderer() {
  const r = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  r.setPixelRatio(1);
  r.setSize(W, H);
  r.shadowMap.enabled = true;
  r.shadowMap.type = THREE.PCFSoftShadowMap;
  r.outputColorSpace = THREE.SRGBColorSpace;
  r.toneMapping = THREE.ACESFilmicToneMapping;
  r.toneMappingExposure = 1.0;
  document.getElementById('stage').appendChild(r.domElement);
  return r;
}

// soft round studio floor that fades into the background
export function floorDisc(radius) {
  const cv = document.createElement('canvas'); cv.width = cv.height = 512;
  const g = cv.getContext('2d');
  const grd = g.createRadialGradient(256, 256, 0, 256, 256, 256);
  grd.addColorStop(0, C.floor); grd.addColorStop(0.65, C.floor); grd.addColorStop(1, C.bg);
  g.fillStyle = grd; g.fillRect(0, 0, 512, 512);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.CircleGeometry(radius, 96), new THREE.MeshBasicMaterial({ map: tex, toneMapped: false }));
  m.rotation.x = -Math.PI / 2;
  const sh = new THREE.Mesh(new THREE.CircleGeometry(radius, 96), new THREE.ShadowMaterial({ opacity: C.shadow }));
  sh.rotation.x = -Math.PI / 2; sh.position.y = 0.001; sh.receiveShadow = true;
  const grp = new THREE.Group(); grp.add(m, sh); return grp;
}

export function lights(scene, accentRim = true) {
  scene.add(new THREE.HemisphereLight(0xffffff, theme === 'dark' ? 0x0b0f14 : 0xdfe6ee, theme === 'dark' ? 0.55 : 1.1));
  const key = new THREE.DirectionalLight(0xffffff, theme === 'dark' ? 2.2 : 2.0);
  key.position.set(2.5, 4, 2.2); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 6; key.shadow.bias = -0.0004;
  Object.assign(key.shadow.camera, { left: -2, right: 2, top: 2, bottom: -2, near: 0.5, far: 12 });
  scene.add(key);
  if (accentRim) {
    const rim = new THREE.DirectionalLight(new THREE.Color(C.accent), theme === 'dark' ? 1.4 : 0.6);
    rim.position.set(-3, 2, -2.5); scene.add(rim);
  }
}

export function fadeLine(points, color, bg, radius = 0.006) {
  // tube along points, color fading from bg (tail) to color (head)
  if (points.length < 2) return null;
  const curve = new THREE.CatmullRomCurve3(points);
  const segs = points.length * 2;
  const geo = new THREE.TubeGeometry(curve, segs, radius, 8, false);
  const cols = [];
  const ca = new THREE.Color(color), cb = new THREE.Color(bg);
  const pos = geo.attributes.position;
  const rings = segs + 1, per = pos.count / rings;
  for (let i = 0; i < rings; i++) {
    const k = Math.pow(i / (rings - 1), 1.6);
    const c = cb.clone().lerp(ca, k);
    for (let j = 0; j < per; j++) cols.push(c.r, c.g, c.b);
  }
  geo.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
  return new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ vertexColors: true, toneMapped: false }));
}

export const css = (extra = '') => {
  const s = document.createElement('style');
  s.textContent = `html,body{margin:0;background:${C.bg};overflow:hidden;width:${W}px;height:${H}px}
  #stage{position:absolute;inset:0}
  #stage::after{content:'';position:absolute;inset:0;pointer-events:none;background:linear-gradient(to bottom, transparent 0%, transparent 72%, ${C.bg} 100%),linear-gradient(to right, transparent 85%, ${C.bg} 100%),linear-gradient(to top, transparent 88%, ${C.bg} 100%)}
  .ov{position:absolute;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display',Inter,'Helvetica Neue',Arial,sans-serif;color:${C.fg};-webkit-font-smoothing:antialiased}
  ${extra}`;
  document.head.appendChild(s);
};

// Left-column title used by every project render, same type as the hero.
export function sideTitle(title, sub) {
  css(`#side{left:${Math.round(72*W/1200)}px;top:0;height:${H}px;display:flex;flex-direction:column;justify-content:center;max-width:430px}
  #side h2{font-size:${Math.round(76*W/1200)}px;line-height:1;margin:0;font-weight:700;letter-spacing:-3px}
  #side .s{font-size:${Math.round(27*W/1200)}px;color:${C.gray};margin-top:18px;letter-spacing:-.3px;line-height:1.3}`);
  const d = document.createElement('div'); d.className = 'ov'; d.id = 'side';
  d.innerHTML = `<h2>${title}</h2><div class="s">${sub}</div>`; document.body.appendChild(d);
}
export function label(id) {
  const d = document.createElement('div'); d.className = 'ov'; d.id = id;
  d.style.cssText = `font-size:20px;font-weight:600;letter-spacing:-.2px;white-space:nowrap;transform:translate(-50%,-100%)`;
  document.body.appendChild(d); return d;
}
export function toScreen(v, cam) { const p = v.clone().project(cam); return { x: (p.x + 1) / 2 * W, y: (1 - p.y) / 2 * H }; }
