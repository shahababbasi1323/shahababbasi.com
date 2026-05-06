function runTool(){
  var input=document.getElementById('tool-input');
  if(!input){return;}
  var text=input.value;
  if(!text.trim()){alert('Please enter some content to analyze.');return;}
  var r=document.getElementById('tool-result');
  r.style.display='block';
  var words=text.trim().split(/\s+/).filter(function(w){return w.length>0;});
  var chars=text.length;
  document.getElementById('tool-output').innerHTML='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;text-align:center;"><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+words.length+'</div><div>Words</div></div><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+chars+'</div><div>Characters</div></div><div><div style="font-size:2rem;font-weight:700;color:#6d28d9;">'+Math.ceil(words.length/200)+' min</div><div>Reading Time</div></div></div><p style="margin-top:1rem;color:#6b7280;">This is a basic analysis. For comprehensive insights, try our professional SEO services.</p>';
}
