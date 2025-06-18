const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const controls = new THREE.PointerLockControls(camera, document.body);

const startButton = document.getElementById('start');
startButton.addEventListener('click', () => {
  controls.lock();
});
controls.addEventListener('lock', () => startButton.style.display = 'none');
controls.addEventListener('unlock', () => startButton.style.display = '');

// Lighting
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1));

// Ground
const groundGeo = new THREE.PlaneGeometry(200, 200);
const groundMat = new THREE.MeshPhongMaterial({ color: 0x555555 });
const ground = new THREE.Mesh(groundGeo, groundMat);
ground.rotation.x = -Math.PI / 2;
scene.add(ground);

// Wingmen
const wingmen = [];
const wingGeo = new THREE.SphereGeometry(0.2, 16, 16);
const wingMat = new THREE.MeshBasicMaterial({ color: 0xff8800 });
for (let i = 0; i < 2; i++) {
  const w = new THREE.Mesh(wingGeo, wingMat);
  scene.add(w);
  wingmen.push(w);
}

let weaponMode = 'machine';
const weaponText = document.getElementById('weapon');
const healthText = document.getElementById('health');
let health = 100;

// Bullets and missiles
const bullets = [];
const missiles = [];
const enemyBullets = [];

// Enemies
const enemies = [];

function spawnEnemy(type) {
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const mat = new THREE.MeshLambertMaterial({ color: type === 'charger' ? 0xff0000 : 0x0000ff });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set((Math.random() - 0.5) * 50, 0.5, -50 - Math.random() * 50);
  scene.add(mesh);
  enemies.push({ type, mesh, hp: 20, cool: 0, pause: 0 });
}

for (let i = 0; i < 5; i++) spawnEnemy('charger');
for (let i = 0; i < 5; i++) spawnEnemy('shooter');

// Input
const keys = {};
window.addEventListener('keydown', e => { keys[e.code] = true; if(e.code === 'Digit1') { weaponMode='machine'; weaponText.textContent='Machine Gun'; } if(e.code==='Digit2'){ weaponMode='laser'; weaponText.textContent='Laser'; } if(e.code==='KeyF'){ fireMissile(); } });
window.addEventListener('keyup', e => { keys[e.code] = false; });

function fireBullet(pos, dir, speed=1, friendly=true) {
  const geo = new THREE.SphereGeometry(0.1, 8, 8);
  const mat = new THREE.MeshBasicMaterial({ color: friendly ? 0xffff00 : 0xff00ff });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.copy(pos);
  scene.add(mesh);
  const arr = friendly ? bullets : enemyBullets;
  arr.push({ mesh, dir: dir.clone(), speed });
}

function fireMissile() {
  const geo = new THREE.ConeGeometry(0.2, 0.5, 8);
  const mat = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.copy(camera.position);
  scene.add(mesh);
  missiles.push({ mesh, target: null, speed: 0.5 });
}

function animate() {
  requestAnimationFrame(animate);

  const delta = 0.1;
  // Movement
  const velocity = new THREE.Vector3();
  if (keys['KeyW']) velocity.z -= 1;
  if (keys['KeyS']) velocity.z += 1;
  if (keys['KeyA']) velocity.x -= 1;
  if (keys['KeyD']) velocity.x += 1;
  velocity.normalize();
  controls.moveRight(velocity.x * delta * 10);
  controls.moveForward(velocity.z * delta * 10);

  // Wingmen orbit
  wingmen.forEach((w,i)=>{
    const angle = performance.now()*0.002 + i*Math.PI;
    w.position.copy(camera.position);
    w.position.x += Math.cos(angle)*1.5;
    w.position.z += Math.sin(angle)*1.5;
  });

  // Firing
  if (keys['Mouse0']) {
    if (weaponMode==='machine') {
      if (Math.random()<0.5) {
        const dir = new THREE.Vector3();
        camera.getWorldDirection(dir);
        dir.x += (Math.random()-0.5)*0.1;
        dir.y += (Math.random()-0.5)*0.1;
        fireBullet(camera.position.clone(), dir, 1.5);
        wingmen.forEach(w=>fireBullet(w.position.clone(), dir, 1.5));
      }
    } else if (weaponMode==='laser') {
      if (Math.random()<0.1) {
        const dir = new THREE.Vector3();
        camera.getWorldDirection(dir);
        fireBullet(camera.position.clone(), dir, 2);
        wingmen.forEach(w=>fireBullet(w.position.clone(), dir, 2));
      }
    }
  }

  // Update bullets
  bullets.forEach((b,idx)=>{
    b.mesh.position.addScaledVector(b.dir, b.speed);
    if (b.mesh.position.distanceTo(camera.position)>100) { scene.remove(b.mesh); bullets.splice(idx,1); }
  });

  // Update missiles
  missiles.forEach((m,idx)=>{
    if(!m.target || m.target.hp<=0) {
      m.target = enemies.find(e=>e.hp>0);
      if(!m.target) { scene.remove(m.mesh); missiles.splice(idx,1); return; }
    }
    const dir = new THREE.Vector3().subVectors(m.target.mesh.position, m.mesh.position).normalize();
    m.mesh.position.addScaledVector(dir, m.speed);
    if (m.mesh.position.distanceTo(m.target.mesh.position)<0.5) {
      m.target.hp -= 10;
      scene.remove(m.mesh);
      missiles.splice(idx,1);
    }
  });

  // Enemy bullets
  enemyBullets.forEach((b,idx)=>{
    b.mesh.position.addScaledVector(b.dir, b.speed);
    if (b.mesh.position.distanceTo(camera.position)>100) { scene.remove(b.mesh); enemyBullets.splice(idx,1); }
    if (b.mesh.position.distanceTo(camera.position)<0.5) {
      health -= 5; healthText.textContent = health; scene.remove(b.mesh); enemyBullets.splice(idx,1); if(health<=0) alert('Game Over');
    }
  });

  // Update enemies
  enemies.forEach((e,idx)=>{
    if(e.hp<=0) { scene.remove(e.mesh); enemies.splice(idx,1); return; }
    if(e.type==='charger') {
      const dir = new THREE.Vector3().subVectors(camera.position, e.mesh.position).setY(0).normalize();
      e.mesh.position.addScaledVector(dir, 0.05);
      if(e.mesh.position.distanceTo(camera.position)<1) { health -=10; healthText.textContent = health; e.hp=0; }
    } else if(e.type==='shooter') {
      if(e.pause>0) { e.pause-=delta; } else {
        if(Math.random()<0.02) e.pause=1+Math.random()*2;
        else {
          const dir = new THREE.Vector3(Math.random()-0.5,0,Math.random()-0.5).normalize();
          e.mesh.position.addScaledVector(dir, 0.05);
        }
      }
      if(e.cool>0) e.cool-=delta; else {
        const dir = new THREE.Vector3().subVectors(camera.position, e.mesh.position).normalize();
        fireBullet(e.mesh.position.clone(), dir, 1, false);
        e.cool=2;
      }
    }
  });

  // Collisions bullet -> enemy
  bullets.forEach((b,bidx)=>{
    enemies.forEach(e=>{
      if(b.mesh.position.distanceTo(e.mesh.position)<0.5) {
        e.hp -= weaponMode==='laser' ? 5 : 2;
        scene.remove(b.mesh);
        bullets.splice(bidx,1);
      }
    });
  });

  renderer.render(scene, camera);
}
animate();

// Mouse input
window.addEventListener('mousedown', ()=>{ keys['Mouse0']=true; });
window.addEventListener('mouseup', ()=>{ keys['Mouse0']=false; });

window.addEventListener('resize', ()=>{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
