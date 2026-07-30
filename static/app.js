let scenarios=[];
let lastResult=null;
let selectedFile=null;
const evidenceGrid=document.querySelector('#evidenceGrid');
const timeline=document.querySelector('#timeline');
const frames=document.querySelector('#frames');
const player=document.querySelector('#mediaPlayer');

const labels={
  visual_ai:['Face manipulation','DeepfakeBench Meso4'],
  voice_ai:['Voice spoof','AASIST'],
  lip_sync:['Audio–visual mismatch','Activity correlation'],
  continuity:['Recording continuity','ResNet-18 embeddings']
};

function scoreTone(value){return value>=65?'risk':value>=50?'warn':''}
function timeLabel(seconds){const s=Math.max(0,Number(seconds)||0);return `00:${String(Math.round(s)).padStart(2,'0')}`}
function setLoading(copy='Running the models locally…'){
  const decision=document.querySelector('#decision');
  decision.textContent='Analysing media';decision.className='decision warn';
  document.querySelector('#decisionCopy').textContent=copy;
  evidenceGrid.innerHTML='<article class="evidence"><h3>Local inference</h3><div class="score">…</div><small>AASIST · Meso4 · ResNet-18</small></article>';
}
function signalCard(name,note,value,available=true){
  const tone=available?scoreTone(value):'warn';
  return `<article class="evidence ${tone}"><div class="evidence-top"><h3>${name}</h3><small>AI signal</small></div><div class="score">${available?value.toFixed(1)+'%':'Abstain'}</div><div class="meter"><span style="width:${available?value:0}%"></span></div><small>${note}</small></article>`;
}
function renderTimeline(result){
  const visual=result.signals.visual_ai||{};
  const items=visual.timeline||result.signals.voice_ai?.segments||[];
  timeline.innerHTML=items.length?items.map((item,index)=>{
    const value=Math.max(item.face_forgery_score||0,item.anomaly_score||0,item.spoof_score||0);
    return `<button class="segment ${scoreTone(value)||'safe'}" style="flex:1" data-start="${item.start_s||0}" title="${item.start_s||0}–${item.end_s||0}s · ${value.toFixed(1)}"></button>`;
  }).join(''):'<span class="muted">No temporal evidence available.</span>';
  document.querySelectorAll('.segment').forEach(el=>el.onclick=()=>{
    document.querySelectorAll('.segment').forEach(x=>x.classList.remove('selected'));el.classList.add('selected');
    player.currentTime=Number(el.dataset.start)||0;player.play().catch(()=>{});
  });
  const top=[...items].sort((a,b)=>Math.max(b.face_forgery_score||0,b.anomaly_score||0)-Math.max(a.face_forgery_score||0,a.anomaly_score||0)).slice(0,3);
  frames.innerHTML=top.length?top.map(item=>`<button class="frame" data-start="${item.start_s||0}"><span>${timeLabel(item.start_s)}</span></button>`).join(''):'<p class="muted">No timestamped visual evidence was available.</p>';
  document.querySelectorAll('.frame').forEach(el=>el.onclick=()=>{player.currentTime=Number(el.dataset.start)||0;player.play().catch(()=>{});});
  document.querySelector('#flagCount').textContent=`${top.length} moment${top.length===1?'':'s'}`;
}
function renderResult(result){
  lastResult=result;
  const visual=result.signals.visual_ai||{available:false};
  const voice=result.signals.voice_ai||{available:false};
  const sync=result.signals.lip_sync||{available:false};
  const continuity=visual.available?Number(visual.continuity_anomaly_top||0):0;
  evidenceGrid.innerHTML=[
    signalCard(...labels.visual_ai,visual.available?Number(visual.score):0,visual.available),
    signalCard(...labels.voice_ai,voice.available?Number(voice.score):0,voice.available),
    signalCard(...labels.lip_sync,sync.available?Number(sync.score):0,sync.available),
    signalCard(...labels.continuity,continuity,visual.available)
  ].join('');
  const map={ESCALATE:['Hold and verify','danger'],REVIEW:['Independent review','warn'],STANDARD:['Continue normal controls','safe'],'INSUFFICIENT EVIDENCE':['Repeat verification','warn']};
  const [title,tone]=map[result.review.level]||[result.review.level,'warn'];
  const decision=document.querySelector('#decision');decision.textContent=title;decision.className=`decision ${tone}`;
  document.querySelector('#decisionCopy').textContent=result.review.action+'. Scores are evidence signals, not fraud probabilities.';
  const video=result.quality.video||{};
  document.querySelector('#qualityValue').textContent=video.sufficient&&result.quality.audio_sufficient?'Usable':'Limited';
  document.querySelector('#mediaDuration').textContent=timeLabel(result.media.duration_s);
  renderTimeline(result);
}
async function analyseScenario(id){
  const scenario=scenarios.find(x=>x.sample_id===id);if(!scenario)return;
  player.src=scenario.media_url;document.querySelector('#caseTitle').textContent=scenario.title;
  document.querySelector('#workflowValue').textContent=scenario.workflow;document.querySelector('#amountValue').textContent=scenario.amount;
  document.querySelector('#labelValue').textContent=scenario.manipulation_type.replaceAll('_',' ');
  setLoading('Running four evidence branches against the selected five-second recording.');
  try{
    const response=await fetch(`/api/scenarios/${id}/analyze`,{method:'POST'});
    const data=await response.json();if(!response.ok)throw new Error(data.error||'Analysis failed');renderResult(data);
  }catch(error){document.querySelector('#decision').textContent='Analysis failed';document.querySelector('#decisionCopy').textContent=error.message;}
}

document.querySelectorAll('.case').forEach(button=>button.onclick=()=>{
  document.querySelectorAll('.case').forEach(x=>x.classList.remove('active'));button.classList.add('active');analyseScenario(button.dataset.case);
});
document.querySelectorAll('.mode').forEach(button=>button.onclick=()=>{
  document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active'));button.classList.add('active');
  document.querySelector('#demoMode').classList.toggle('hidden',button.dataset.mode!=='demo');document.querySelector('#uploadMode').classList.toggle('hidden',button.dataset.mode!=='upload');
});
const input=document.querySelector('#fileInput');input.onchange=()=>{
  if(!input.files[0])return;selectedFile=input.files[0];document.querySelector('#dropzone').classList.add('hidden');document.querySelector('#fileReady').classList.remove('hidden');
  document.querySelector('#fileName').textContent=selectedFile.name;document.querySelector('#fileSize').textContent=`${(selectedFile.size/1024/1024).toFixed(2)} MB · Ready for local analysis`;
};
document.querySelector('#analyseBtn').onclick=async()=>{
  if(!selectedFile)return;document.querySelector('#uploadStatus').textContent='Analysing locally…';setLoading();
  const form=new FormData();form.append('file',selectedFile);form.append('context',JSON.stringify({workflow:'uploaded approval'}));
  try{
    const response=await fetch('/api/analyze',{method:'POST',body:form});const data=await response.json();if(!response.ok)throw new Error(data.error||'Analysis failed');
    document.querySelector('.mode[data-mode="demo"]').click();player.src=URL.createObjectURL(selectedFile);document.querySelector('#caseTitle').textContent=selectedFile.name;
    document.querySelector('#workflowValue').textContent='Uploaded approval';document.querySelector('#amountValue').textContent='User supplied';document.querySelector('#labelValue').textContent='Unknown';renderResult(data);
  }catch(error){document.querySelector('#uploadStatus').textContent=error.message;}
};
document.querySelector('#downloadBtn').onclick=()=>{
  if(!lastResult)return;const blob=new Blob([JSON.stringify(lastResult,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='approvalguard-evidence.json';a.click();URL.revokeObjectURL(a.href);
};

fetch('/api/scenarios').then(r=>r.json()).then(data=>{scenarios=data;analyseScenario('video_tampered_01')}).catch(error=>{document.querySelector('#decisionCopy').textContent=error.message});
