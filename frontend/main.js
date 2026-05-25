const API_BASE = window.localStorage.getItem('api_base') || 'http://localhost:8000';

const tokenStore = {
  get access(){return localStorage.getItem('access_token')},
  get refresh(){return localStorage.getItem('refresh_token')},
  set(access, refresh){ if(access) localStorage.setItem('access_token',access); if(refresh) localStorage.setItem('refresh_token',refresh); },
  clear(){localStorage.removeItem('access_token');localStorage.removeItem('refresh_token');localStorage.removeItem('me');}
};

let refreshPromise = null;
async function refreshAccessToken(){
  if(refreshPromise) return refreshPromise;
  const refresh = tokenStore.refresh;
  if(!refresh) throw new Error('No refresh token');
  refreshPromise = fetch(`${API_BASE}/api/token/refresh/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh})})
    .then(async r=>{if(!r.ok) throw new Error('Refresh failed'); const d=await r.json(); tokenStore.set(d.access, refresh); return d.access;})
    .finally(()=> refreshPromise=null);
  return refreshPromise;
}

async function api(path, opts={}){
  const headers = {'Content-Type':'application/json', ...(opts.headers||{})};
  if(tokenStore.access) headers.Authorization = `Bearer ${tokenStore.access}`;
  let res = await fetch(`${API_BASE}${path}`, {...opts, headers});
  if(res.status===401 && tokenStore.refresh){
    try{ await refreshAccessToken(); headers.Authorization=`Bearer ${tokenStore.access}`; res=await fetch(`${API_BASE}${path}`,{...opts,headers}); }
    catch(e){ tokenStore.clear(); renderLogin(); throw e; }
  }
  if(!res.ok) throw await res.json().catch(()=>({detail:'API xato'}));
  return res.json();
}

const app=document.getElementById('app');

function topBar(){return `<div class='top'><div style='font-size:46px;line-height:0.8'>bir<span style='color:#50db68'>b</span>ir</div><div>Toshkent &nbsp; UZ</div></div>`}

function nav(){return `<div class='container'><div class='row'><button class='btn' id='open-cats'>Kategoriyalar</button><input class='search' id='search' placeholder='iPhone 15 Pro topish'/><button class='btn' id='go-fav'>Sevimlilar</button><button class='btn' id='go-profile'>Profil</button><button class='btn' id='go-create'>Sotish +</button><button class='btn' id='logout'>Chiqish</button></div></div>`}

function listingCard(i){
  const img=i.images?.[0]?.image||'';
  return `<div class='listing'><img src='${img}'/><div class='p'><b>${i.title||"Nomsiz"}</b><div class='muted'>${i.price||''}</div><div class='muted'>${i.region?.name||''}</div><button class='btn fav' data-id='${i.id}'>Saqlash</button></div></div>`;
}

async function renderHome(){
  app.innerHTML = topBar()+nav()+`<div class='container'><h1>Toshkentda e'lonlar: xarid va sotuv BirBir orqali</h1><div id='cats' class='grid section'></div><h2 class='section'>E'lonlar</h2><div id='listings' class='listings'></div></div>`;
  bindGlobal();
  const [cats, listings] = await Promise.all([fetch(`${API_BASE}/categories/`).then(r=>r.json()), fetch(`${API_BASE}/elonlar/`).then(r=>r.json())]);
  const catEl=document.getElementById('cats');
  const arr=Array.isArray(cats)?cats:cats.results||[];
  catEl.innerHTML=arr.slice(0,12).map(c=>`<div class='card'><b>${c.name||c.title||'Kategoriya'}</b></div>`).join('') + `<div class='card'><b>Barcha kategoriyalar →</b></div>`;
  const list = listings.results || listings || [];
  document.getElementById('listings').innerHTML=list.map(listingCard).join('');
  document.querySelectorAll('.fav').forEach(b=>b.onclick=()=>toggleFavorite(b.dataset.id));
}

async function renderProfile(){
  const me = await api('/accounts/me/');
  app.innerHTML = topBar()+nav()+`<div class='container layout'><div class='sidebar'><h2>${me.username||''}</h2><div class='muted'>${me.phone_number||''}</div><hr/><button class='btn menu' data-v='fav'>Sevimlilar</button><button class='btn menu' data-v='my'>Mening e'lonlarim</button><button class='btn menu' data-v='edit'>Profilni tahrirlash</button></div><div class='main' id='profile-content'></div></div>`;
  bindGlobal();
  document.querySelectorAll('.menu').forEach(b=>b.onclick=()=>profileTab(b.dataset.v, me));
  profileTab('fav',me);
}

async function profileTab(tab, me){
  const el=document.getElementById('profile-content');
  if(tab==='fav'){
    const fav=await api('/favorites/'); const list=fav.results||fav||[];
    el.innerHTML=`<h2>Sevimlilar</h2>${list.length?list.map(x=>`<div class='card'>${x.favorite_listing?.title||x.id}</div>`).join(''):`<p class='muted'>Bo'sh</p>`}`;
  }else if(tab==='my'){
    const ls=await fetch(`${API_BASE}/elonlar/`,{headers:{Authorization:`Bearer ${tokenStore.access}`}}).then(r=>r.json());
    const list=(ls.results||ls||[]).filter(x=>x.user?.id===me.id);
    el.innerHTML=`<h2>Mening e'lonlarim</h2>${list.map(listingCard).join('')||"<p class='muted'>Yo'q</p>"}`;
  }else{
    el.innerHTML=`<h2>Profilni tahrirlash</h2><input class='input' id='u' value='${me.username||''}'/><textarea id='bio'>${me.bio||''}</textarea><button class='btn' id='save'>Saqlash</button>`;
    document.getElementById('save').onclick=async()=>{await api(`/accounts/profile/update/${me.id}/`,{method:'PATCH',body:JSON.stringify({username:document.getElementById('u').value,bio:document.getElementById('bio').value})});alert('Saqlandi')};
  }
}

async function renderCreate(){
  const cats = await fetch(`${API_BASE}/categories/`).then(r=>r.json());
  const regions = await fetch(`${API_BASE}/elonlar/regions/`).then(r=>r.json());
  const catArr=Array.isArray(cats)?cats:cats.results||[]; const regArr=Array.isArray(regions)?regions:regions.results||[];
  app.innerHTML=topBar()+nav()+`<div class='container'><h1>Yangi e'lon</h1>
    <div class='form-card'><label>Nom</label><input class='input' id='title'/></div>
    <div class='form-card'><label>Kategoriya</label><select id='cat'>${catArr.map(c=>`<option value='${c.id}'>${c.name||c.title}</option>`).join('')}</select></div>
    <div class='form-card'><label>Narx</label><input class='input' id='price'/></div>
    <div class='form-card'><label>Tavsif</label><textarea id='desc'></textarea></div>
    <div class='form-card'><label>Region</label><select id='region'>${regArr.map(r=>`<option value='${r.slug}'>${r.name}</option>`).join('')}</select><select id='district'></select></div>
    <div class='form-card'><label>Aloqa</label><input class='input' id='phone' placeholder='+998...'/><input class='input' id='name' placeholder='Ism'/></div>
    <button class='btn' id='submit'>Joylash</button>
  </div>`;
  bindGlobal();
  const loadDistricts=async()=>{const slug=document.getElementById('region').value; const d=await fetch(`${API_BASE}/elonlar/regions/${slug}/districts/`).then(r=>r.json()); const arr=d.results||d||[]; document.getElementById('district').innerHTML=arr.map(x=>`<option value='${x.id}'>${x.name}</option>`).join('')};
  document.getElementById('region').onchange=loadDistricts; await loadDistricts();
  document.getElementById('submit').onclick=async()=>alert('Backendga mos multipart payloadni shu formdan yuborasiz. API yoqlari uchun frontend tayyor.');
}

function renderLogin(){
  app.innerHTML = topBar()+`<div class='container'><div class='form-card' style='max-width:440px;margin:auto'><h2>Login</h2><input class='input' id='identifier' placeholder='email yoki phone'/><input type='password' class='input' id='password' placeholder='password' style='margin-top:8px'/><button class='btn' id='login' style='margin-top:10px'>Kirish</button></div></div>`;
  document.getElementById('login').onclick=async()=>{
    try{const d=await fetch(`${API_BASE}/api/auth/login/`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({identifier:identifier.value,password:password.value})}).then(r=>r.json());
      tokenStore.set(d.access,d.refresh); localStorage.setItem('me',JSON.stringify(d.user)); renderHome();}catch{alert('Login xato')}
  }
}

async function toggleFavorite(id){
  try{await api('/favorites/create/',{method:'POST',body:JSON.stringify({favorite_listing:id})}); alert('Sevimliga qo`shildi/olindi');}
  catch(e){alert(e.detail||'Xato')}
}

function bindGlobal(){
  document.getElementById('go-profile').onclick=renderProfile;
  document.getElementById('go-create').onclick=renderCreate;
  document.getElementById('go-fav').onclick=()=>renderProfile().then(()=>profileTab('fav', JSON.parse(localStorage.getItem('me')||'{}')));
  document.getElementById('logout').onclick=()=>{tokenStore.clear();renderLogin();};
  document.getElementById('open-cats').onclick=()=>window.scrollTo({top:320,behavior:'smooth'});
  document.getElementById('search').onkeydown=(e)=>{if(e.key==='Enter') location.href='#search='+encodeURIComponent(e.target.value)};
}

if(tokenStore.access) renderHome(); else renderLogin();
