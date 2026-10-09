// ===== CONFIG: replace the booking link here =====
const CONFIG = { BOOKING_URL: 'https://t.me/astroyogaN', CHANNEL_URL: 'https://t.me/astroyogaN' };
document.querySelectorAll('.js-book').forEach(a=>{a.href=CONFIG.BOOKING_URL;a.target='_blank';a.rel='noopener'});
document.querySelectorAll('.js-channel').forEach(a=>{a.href=CONFIG.CHANNEL_URL;a.target='_blank';a.rel='noopener'});
document.getElementById('y').textContent=new Date().getFullYear();
const hdr=document.querySelector('.hdr'),burger=document.querySelector('.burger');
burger.addEventListener('click',()=>{const o=hdr.classList.toggle('open');burger.setAttribute('aria-expanded',o)});
document.querySelectorAll('.nav a').forEach(a=>a.addEventListener('click',()=>hdr.classList.remove('open')));
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
const px=[...document.querySelectorAll('[data-parallax]')],rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
let tick=false;
addEventListener('scroll',()=>{hdr.classList.toggle('scrolled',scrollY>20);
 if(rm||tick)return;tick=true;requestAnimationFrame(()=>{px.forEach(el=>el.style.transform=`translate3d(0,${scrollY*el.dataset.parallax}px,0)`);tick=false})},{passive:true});
