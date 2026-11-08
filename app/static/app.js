document.querySelectorAll('form[data-confirm]').forEach(form=>form.addEventListener('submit',event=>{if(!confirm(form.dataset.confirm))event.preventDefault();}));
const rows=document.querySelector('#product-rows');
if(rows){
 const preview=()=>{let total=0;rows.querySelectorAll('.product-row').forEach(row=>{const option=row.querySelector('select').selectedOptions[0];total+=Number(option?.dataset.price||0)*Number(row.querySelector('input').value||0);});document.querySelector('#total-preview').textContent=new Intl.NumberFormat('id-ID',{style:'currency',currency:'IDR',maximumFractionDigits:0}).format(total);};
 rows.addEventListener('input',preview);
 rows.addEventListener('click',event=>{if(event.target.matches('[data-remove]')&&rows.children.length>1){event.target.closest('.product-row').remove();preview();}});
 document.querySelector('#add-item').addEventListener('click',()=>{const row=rows.firstElementChild.cloneNode(true);row.querySelector('select').selectedIndex=0;row.querySelector('input').value=1;rows.append(row);preview();});preview();
}
