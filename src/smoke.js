// smoke test: run the viewer script against stub DOM/THREE to catch reference and type errors
const fs=require('fs');const h=fs.readFileSync('out/index.html','utf8');const src=h.split('<script>')[1].split('</script>')[0];
const handlers={};
function U(){const f=function(){return U();};return new Proxy(f,{get(t,k){if(k===Symbol.toPrimitive)return()=>1;if(k==='length')return 0;if(k==='x'||k==='y'||k==='z'||k==='width'||k==='clientWidth'||k==='clientHeight')return 100;if(k==='forEach')return()=>{};if(k==='matches')return false;if(k==='trim')return()=>'#fff';return U();},set(){return true;},construct(){return U();},apply(){return U();}});}
const els={};
function el(id){const e={id,style:{},attrs:{},children:[],setAttribute(k,v){this.attrs[k]=v;},getAttribute(k){return this.attrs[k];},
  addEventListener(ev,fn){(handlers[id||'_']=handlers[id||'_']||{})[ev]=fn;},appendChild(c){this.children.push(c);},getContext(){return U();},setPointerCapture(){},clientWidth:800,clientHeight:600,width:0,height:0,textContent:'',value:'',size:0,blur(){}};return e;}
global.document={getElementById(id){return els[id]||(els[id]=el(id));},createElement(){return el();},createTextNode(){return {};},querySelectorAll(){return [];},documentElement:{}};
global.window=global;global.THREE=new Proxy({},{get(){return function(){return U();};}});
global.getComputedStyle=()=>({getPropertyValue:()=>'#dcdbd7'});global.MutationObserver=function(){return {observe(){}};};global.ResizeObserver=function(){return {observe(){}};};
let frames=0;global.requestAnimationFrame=(f)=>{if(frames++<3)f(16*frames);};global.performance={now:()=>0};global.localStorage={getItem:()=>null,setItem(){}};
window.matchMedia=()=>({matches:false,addEventListener(){}});window.addEventListener=()=>{};window.devicePixelRatio=1;
new Function(src)();
// click through floors, toggles and every view
['f-2','t-dims','t-zones','t-rooms','t-elec','t-ceil','t-furn','t-edge','f-1','t-zones','f-2','f-1'].forEach(id=>{if(!handlers[id]||!handlers[id].click)throw new Error('no click handler: '+id);handlers[id].click();});
console.log('smoke ok; pressed f-1:',els['f-1'].attrs['aria-pressed'],'f-2:',els['f-2'].attrs['aria-pressed'],'err box:',JSON.stringify(els['err'].textContent));
