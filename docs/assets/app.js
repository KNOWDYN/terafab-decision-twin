
const panelCopy = {
  power: 'Power module: models process load, facility overhead, cooling energy, peak stress, and annual energy.',
  water: 'Water module: separates withdrawal, consumption, reuse fraction, cooling sensitivity, and regional burden.',
  exergy: 'Exergy module: quantifies destroyed useful work potential and identifies thermodynamic leverage points.',
  yield: 'Yield module: prevents nominal capacity from being confused with qualified saleable output.',
  economics: 'Economics module: translates energy, water, yield, capex, opex, uncertainty, and policy friction into decision variables.',
  policy: 'Policy module: converts outputs into grid, water, readiness, subsidy, permitting, and industrial-strategy questions.'
};
const scenarios = {
  baseline: {title:'2026 baseline', tag:'evidence-gated assumption set', body:'Single-period baseline used to test schema completeness, conservation checks, reporting, and gate behavior. It is not a claim of verified Terafab operation.', outputs:['load and energy balance','water withdrawal/consumption estimate','readiness and evidence gates','policy questions']},
  stress: {title:'1 TW stress test', tag:'stress-test assumption, not verified site load', body:'Extreme scenario for understanding power, cooling, water, exergy, and grid-system sensitivity at terawatt scale.', outputs:['grid stress index','cooling and heat-rejection burden','water reuse sensitivity','exergy destruction signal']},
  multi: {title:'Multi-year path', tag:'forward-looking scenario', body:'Time-indexed scenario structure for comparing ramp, readiness, yield learning, energy intensity, water reuse, and policy exposure across years.', outputs:['annual vectors','ramp and learning effects','option value','policy gate evolution']}
};
function renderScenario(key='baseline'){
  const target = document.getElementById('scenarioOutput'); if(!target) return;
  const s = scenarios[key];
  target.innerHTML = `<h3>${s.title}</h3><span class="status-pill">${s.tag}</span><p>${s.body}</p><ul>${s.outputs.map(x=>`<li>${x}</li>`).join('')}</ul>`;
}
document.addEventListener('click', e=>{
  const mapBtn=e.target.closest('[data-panel]');
  if(mapBtn){document.querySelectorAll('[data-panel]').forEach(b=>b.classList.remove('active'));mapBtn.classList.add('active');const p=document.getElementById('mapPanel');if(p)p.textContent=panelCopy[mapBtn.dataset.panel];}
  const tab=e.target.closest('[data-scenario]');
  if(tab){document.querySelectorAll('[data-scenario]').forEach(t=>t.classList.remove('active'));tab.classList.add('active');renderScenario(tab.dataset.scenario);}
  const copy=e.target.closest('[data-copy]');
  if(copy){navigator.clipboard?.writeText(copy.dataset.copy).then(()=>{const old=copy.textContent;copy.textContent='Copied';setTimeout(()=>copy.textContent=old,1200);});}
  const nav=e.target.closest('.nav-toggle');
  if(nav){const links=document.getElementById('site-nav');const open=!links.classList.contains('open');links.classList.toggle('open',open);nav.setAttribute('aria-expanded',String(open));}
});
renderScenario('baseline');
let deferredPrompt;
window.addEventListener('beforeinstallprompt', event=>{event.preventDefault();deferredPrompt=event;const btn=document.getElementById('installButton');if(btn) btn.hidden=false;});
document.getElementById('installButton')?.addEventListener('click', async()=>{if(!deferredPrompt)return;deferredPrompt.prompt();await deferredPrompt.userChoice;deferredPrompt=null;document.getElementById('installButton').hidden=true;});
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('./service-worker.js',{scope:'./'}).catch(()=>{}));}
