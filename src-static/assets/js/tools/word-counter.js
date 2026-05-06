function runTool(){
  var t=document.getElementById('tool-input').value;
  if(!t.trim()){alert('Please enter some text.');return;}
  var words=t.trim().split(/\s+/).filter(function(w){return w.length>0;});
  var chars=t.length;
  var charsNoSpace=t.replace(/\s/g,'').length;
  var sentences=t.split(/[.!?]+/).filter(function(s){return s.trim().length>0;});
  var paragraphs=t.split(/\n\n+/).filter(function(p){return p.trim().length>0;});
  var readTime=Math.ceil(words.length/200);
  var r=document.getElementById('tool-result');
  r.style.display='block';
  document.getElementById('tool-output').innerHTML='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;text-align:center;"><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+words.length+'</div><div>Words</div></div><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+chars+'</div><div>Characters</div></div><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+charsNoSpace+'</div><div>Chars (no spaces)</div></div><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+sentences.length+'</div><div>Sentences</div></div><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+paragraphs.length+'</div><div>Paragraphs</div></div><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+readTime+' min</div><div>Reading Time</div></div></div>';
}
