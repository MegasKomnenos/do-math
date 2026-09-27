"use strict";
document.documentElement.classList.add("js");
document.querySelectorAll(".quiz").forEach(quiz => {
 const feedback=quiz.querySelector(".feedback");
 quiz.querySelectorAll("button[data-choice]").forEach(button => button.addEventListener("click",()=>{
  const correct=button.dataset.choice===quiz.dataset.answer;
  quiz.querySelectorAll("button[data-choice]").forEach(other=>other.setAttribute("aria-pressed",String(other===button)));
  feedback.className="feedback "+(correct?"ok":"retry");
  feedback.textContent=(correct?"정확합니다. ":"다시 대조해 보세요. ")+quiz.dataset.explain;
 }));
});
document.querySelectorAll("[data-walkthrough]").forEach(walk=>{
 const steps=Array.from(walk.querySelectorAll("[data-step]"));let index=0;
 const previous=walk.querySelector("[data-prev]"),next=walk.querySelector("[data-next]"),position=walk.querySelector("[data-position]");
 function render(){steps.forEach((step,i)=>step.hidden=i!==index);previous.disabled=index===0;next.disabled=index===steps.length-1;position.textContent=(index+1)+" / "+steps.length+" 사건";}
 previous.addEventListener("click",()=>{if(index>0){index--;render();}});
 next.addEventListener("click",()=>{if(index<steps.length-1){index++;render();}});
 render();
});
const search=document.querySelector("[data-glossary-search]");
if(search){search.addEventListener("input",()=>{const q=search.value.trim().toLocaleLowerCase("ko");let count=0;document.querySelectorAll(".glossary-entry").forEach(entry=>{entry.hidden=!entry.textContent.toLocaleLowerCase("ko").includes(q);if(!entry.hidden)count++;});document.querySelector("[data-search-status]").textContent=count+"개 용어";});}
document.querySelectorAll("[data-quantifier]").forEach(widget=>{const input=widget.querySelector("input"),output=widget.querySelector("output");function update(){output.textContent="x = "+input.value+" 이면 y = "+input.value+" 를 선택";}input.addEventListener("input",update);update();});

const catalogSearch=document.querySelector('[data-catalog-search]');
if(catalogSearch){catalogSearch.addEventListener('input',()=>{let count=0;const q=catalogSearch.value.trim().toLowerCase();document.querySelectorAll('[data-catalog-row]').forEach(row=>{row.hidden=!row.textContent.toLowerCase().includes(q);if(!row.hidden)count++;});document.querySelector('[data-catalog-count]').textContent=count+'개 파일';});}
document.querySelectorAll('.table-wrap').forEach(el=>{el.tabIndex=0;el.setAttribute('aria-label','가로로 이동할 수 있는 표');});
let printClosed=[];
addEventListener('beforeprint',()=>{printClosed=[...document.querySelectorAll('details:not([open])')];printClosed.forEach(x=>x.open=true);});
addEventListener('afterprint',()=>{printClosed.forEach(x=>x.open=false);printClosed=[];});
