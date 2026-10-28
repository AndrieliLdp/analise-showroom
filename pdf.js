/* Botão "Baixar PDF": gera um PDF da aba que está na tela (cabeçalho, filtros, indicadores e gráficos). */
(function(){
  var st=document.createElement("style");
  st.textContent=".hero{position:relative}"+
    ".pdfbtn{position:absolute;top:28px;right:32px;display:inline-flex;align-items:center;gap:8px;background:var(--gold);color:#1d2560;border:0;border-radius:999px;padding:10px 20px;font:700 14px var(--body);cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.18)}"+
    ".pdfbtn:hover{filter:brightness(1.06)}.pdfbtn:focus-visible{outline:3px solid #fff;outline-offset:2px}.pdfbtn[disabled]{opacity:.65;cursor:wait}"+
    "@media (max-width:640px){.pdfbtn{position:static;margin-top:18px}}";
  document.head.appendChild(st);
  var hero=document.querySelector(".hero"); if(!hero) return;
  var b=document.createElement("button");
  b.type="button"; b.id="pdfBtn"; b.className="pdfbtn"; b.setAttribute("data-html2canvas-ignore","");
  var LABEL='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>Baixar PDF';
  b.innerHTML=LABEL; hero.appendChild(b);
  b.addEventListener("click", async function(){
    if(!window.html2canvas||!window.jspdf){alert("Não foi possível carregar o gerador de PDF. Verifique a internet e tente de novo.");return}
    b.disabled=true; b.textContent="Gerando PDF…";
    try{
      var aba=document.querySelector('.tab[aria-selected="true"] strong');
      var nome=(aba?aba.textContent:"Dashboard").normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/[^A-Za-z0-9]+/g,"_").replace(/^_|_$/g,"");
      var el=document.querySelector(".wrap");
      var canvas=await html2canvas(el,{scale:2,backgroundColor:getComputedStyle(document.body).backgroundColor,useCORS:true,logging:false});
      var w=canvas.width/2, h=canvas.height/2;
      var pdf=new window.jspdf.jsPDF({orientation:w>h?"landscape":"portrait",unit:"px",format:[w,h],hotfixes:["px_scaling"],compress:true});
      pdf.addImage(canvas.toDataURL("image/jpeg",0.92),"JPEG",0,0,w,h);
      var d=new Date(), p=function(n){return String(n).padStart(2,"0")};
      pdf.save("Analise_Showroom_"+nome+"_"+p(d.getDate())+"-"+p(d.getMonth()+1)+"-"+d.getFullYear()+".pdf");
    }catch(e){alert("Não foi possível gerar o PDF: "+(e&&e.message||e))}
    finally{b.disabled=false; b.innerHTML=LABEL}
  });
})();
