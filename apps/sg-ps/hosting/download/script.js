const previewNames={horix:'HORIX',vectors:'HORIX Vectors',light:'HORIX Light',layout:'HORIX Layout'};
let currentPreview='horix';
const dialog=document.querySelector('.preview-dialog');
const mobileButton=document.querySelector('.mobile-menu');
const mobileNav=document.querySelector('.mobile-nav');
mobileButton.addEventListener('click',()=>{const expanded=mobileButton.getAttribute('aria-expanded')==='true';mobileButton.setAttribute('aria-expanded',String(!expanded));mobileButton.setAttribute('aria-label',expanded?'افتح القائمة':'أغلق القائمة');mobileNav.hidden=expanded;});
mobileNav.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{mobileNav.hidden=true;mobileButton.setAttribute('aria-expanded','false');mobileButton.setAttribute('aria-label','افتح القائمة');}));
function setPreview(id){currentPreview=id;document.querySelector('#hero-screen').src=`assets/screens/${id}.webp`;document.querySelectorAll('[data-preview]').forEach(button=>button.setAttribute('aria-selected',String(button.dataset.preview===id)));}
document.querySelectorAll('[data-preview]').forEach(button=>button.addEventListener('click',()=>setPreview(button.dataset.preview)));
function fullPreview(id){const image=document.querySelector('#full-preview');image.src=`assets/screens/${id}.webp`;image.alt=`تصور الواجهة الجديدة لـ ${previewNames[id]}`;dialog.showModal();}
document.querySelector('.expand-preview').addEventListener('click',()=>fullPreview(currentPreview));
document.querySelectorAll('[data-full-preview]').forEach(button=>button.addEventListener('click',()=>fullPreview(button.dataset.fullPreview)));
document.querySelector('.close-dialog').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)dialog.close();}});
function selectPlatform(id){document.querySelectorAll('[data-platform]').forEach(button=>button.setAttribute('aria-selected',String(button.dataset.platform===id)));document.querySelector('#panel-windows').hidden=id!=='windows';document.querySelector('#panel-mac').hidden=id!=='mac';}
document.querySelectorAll('[data-platform]').forEach(button=>button.addEventListener('click',()=>selectPlatform(button.dataset.platform)));
document.querySelectorAll('[data-select-mac]').forEach(link=>link.addEventListener('click',()=>selectPlatform('mac')));
for(const selector of ['.preview-tabs','.platform-tabs']){
  const list=document.querySelector(selector);
  list.addEventListener('keydown',event=>{const buttons=[...list.querySelectorAll('button')];const current=buttons.indexOf(document.activeElement);if(current<0)return;let next;if(event.key==='ArrowRight')next=(current+1)%buttons.length;else if(event.key==='ArrowLeft')next=(current-1+buttons.length)%buttons.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=buttons.length-1;else return;event.preventDefault();buttons[next].focus();buttons[next].click();});
}
// Coming-soon apps: the WhatsApp waitlist (waitlist.php, deployed next to this page by build.sh).
const form=document.querySelector('#waitlist-form');
const error=document.querySelector('#form-error');
const result=document.querySelector('.form-result');
form.addEventListener('submit',event=>{
  event.preventDefault();error.textContent='';result.hidden=true;
  const name=form.elements.name.value.trim();const phone=form.elements.phone.value.trim();const digits=phone.replace(/\D/g,'');
  const products=[...form.querySelectorAll('[name=products]:checked')].map(box=>box.value);
  if(!name){error.textContent='اكتب اسمك الأول.';form.elements.name.focus();return;}
  if(digits.length<8||digits.length>15){error.textContent='اكتب رقم واتساب صحيح.';form.elements.phone.focus();return;}
  if(!products.length){error.textContent='اختار مجال واحد على الأقل.';return;}
  if(!form.elements.consent.checked){error.textContent='محتاجين موافقتك قبل التواصل على واتساب.';form.elements.consent.focus();return;}
  const button=form.querySelector('button[type=submit]');button.disabled=true;
  fetch('waitlist.php',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,phone,products,interests:[],consent:true,page:location.pathname})})
    .then(response=>response.json().catch(()=>null).then(body=>[response.status,body]))
    .then(([status,body])=>{
      if(body&&body.ok){[...form.children].forEach(child=>{if(child!==result&&!child.classList.contains('form-heading'))child.hidden=true;});result.hidden=false;}
      else if(status===429)error.textContent='طلبات كتير من نفس الجهاز، جرّب كمان شوية.';
      else error.textContent='حصلت مشكلة في الإرسال، جرّب تاني.';
    })
    .catch(()=>{error.textContent='مفيش اتصال بالإنترنت، جرّب تاني.';})
    .finally(()=>{button.disabled=false;});
});
// Open the visitor's platform first (a Mac gets the macOS tab; everyone else Windows).
const ua=navigator.userAgent||'';
if(/Macintosh/.test(ua)&&!/Mobile/.test(ua)&&!(navigator.maxTouchPoints>1))selectPlatform('mac');
const megabytes=bytes=>`${(bytes/1048576).toFixed(bytes<10485760?1:0)} MB`;
// HORIX Launcher: the newest release from the feed the launcher itself reads (same site).
// The static href and text in the page stay as the fallback.
fetch('launcher/release_info.json',{cache:'no-store'}).then(response=>response.ok?response.json():null).then(data=>{
  const release=data?.release_info?.apps?.['horix-launcher']?.latest_release;
  const asset=release?.assets?.find(item=>item.name.endsWith('-windows-x64-portable.zip'));
  if(!asset)return;const url=new URL(asset.download_url,location.href);if(url.protocol!=='https:')return;
  document.querySelector('#windows-download').href=url.href;
  document.querySelector('[data-windows-version]').textContent=`v${release.version}`+(asset.size_bytes?` · ${megabytes(asset.size_bytes)}`:'');
}).catch(()=>{});
// Mac: each app's disk image on this site (mac/latest.json: version, file and size per app).
fetch('mac/latest.json',{cache:'no-store'}).then(response=>response.ok?response.json():null).then(data=>{
  if(!data)return;document.querySelectorAll('[data-mac-id]').forEach(link=>{
    const file=data[link.dataset.macId];if(!file||!/^[-\w.]+\.dmg$/.test(file.file||''))return;
    link.href=`mac/${encodeURIComponent(file.file)}?v=${encodeURIComponent(file.version)}`;
    link.querySelector('[data-mac-size]').textContent=`v${file.version}`+(file.size?` · ${megabytes(file.size)}`:'');
  });
}).catch(()=>{});
