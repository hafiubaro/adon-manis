// Jalankan hanya pada database demonstrasi kosong yang sudah diisi seed_demo.py.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{
const out=path.resolve('evidence/module8');fs.mkdirSync(out,{recursive:true});
const checks=[];function ok(name,v){if(!v)throw Error(name);checks.push({name,passed:true});}
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE_PATH?{executablePath:process.env.CHROMIUM_EXECUTABLE_PATH}:{}),args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
const page=await browser.newPage({viewport:{width:1440,height:1050}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
const base=process.env.APP_URL||'http://127.0.0.1:5000';
async function shot(name){await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});}
async function signin(user,pass){await page.goto(base+'/login');await page.locator('[name=username]').fill(user);await page.locator('[name=password]').fill(pass);await page.getByRole('button',{name:'Masuk ke ruang kerja',exact:true}).click();await page.waitForURL(base+'/');}
await signin('admin',process.env.E2E_ADMIN_PASSWORD);ok('Login admin',await page.locator('h1').innerText()==='Ringkasan pesanan');
await shot('01_dashboard_awal');ok('Nilai awal Rp180000',(await page.locator('.stat.featured').innerText()).includes('Rp180.000'));
await page.goto(base+'/pesanan/baru');await page.locator('#id_pelanggan').selectOption('1');await page.locator('#id_channel').selectOption('1');await page.locator('[name=id_produk]').selectOption('1');await page.locator('[name=jumlah]').fill('2');await page.locator('#add-item').click();await page.locator('[name=id_produk]').nth(1).selectOption('3');await page.locator('[name=jumlah]').nth(1).fill('1');
ok('Estimasi multi item Rp65000',(await page.locator('#total-preview').innerText()).replace(/\s/g,'').includes('65.000'));
await shot('02_form_multi_item');await page.getByRole('button',{name:'Simpan pesanan',exact:true}).click();await page.waitForURL(/\/pesanan\/\d+$/);const detail=page.url(),code=await page.locator('h1').innerText();
ok('Pesanan tersimpan dengan dua detail',await page.locator('.two-col > div').first().locator('section').first().locator('tbody tr').count()===2);await shot('03_detail_diterima');
await page.goto(base+'/');ok('Dashboard diterima bertambah menjadi4',(await page.locator('.stat').first().locator('strong').innerText())==='4');ok('Nilai selesai belum berubah',(await page.locator('.stat.featured').innerText()).includes('Rp180.000'));
await page.goto(base+'/pesanan?q='+code+'&channel=1&status=diterima');ok('Pencarian dan filter menemukan satu pesanan',await page.locator('tbody tr').count()===1 && (await page.locator('tbody').innerText()).includes(code));await shot('04_filter_pesanan');
await page.goto(detail);await page.getByRole('button',{name:'Mulai diproses',exact:true}).click();await page.getByRole('button',{name:'Tandai selesai',exact:true}).click();ok('Status selesai dan tiga log',await page.locator('section').filter({has:page.getByRole('heading',{name:'Riwayat status'})}).locator('tbody tr').count()===3);await shot('05_detail_selesai');
await page.goto(base+'/');ok('Dashboard selesai menjadi4',await page.locator('.stat').nth(2).locator('strong').innerText()==='4');ok('Nilai selesai menjadiRp245000',(await page.locator('.stat.featured').innerText()).includes('Rp245.000'));await shot('06_dashboard_akhir');
await page.goto(base+'/laporan');ok('Laporan 11 pesanan',await page.getByTestId('report-count').innerText()==='11 pesanan');ok('Laporan nilaiRp245000',await page.getByTestId('report-value').innerText()==='Rp245.000');await shot('07_laporan');
await page.pdf({path:path.join(out,'laporan_cetak.pdf'),format:'A4',printBackground:true});ok('PDF tercetak',fs.statSync(path.join(out,'laporan_cetak.pdf')).size>1000);
await page.getByRole('button',{name:'Keluar',exact:true}).click();await signin('pemilik',process.env.E2E_OWNER_PASSWORD);await page.goto(base+'/laporan?basis=selesai');ok('Pemilik membaca laporan selesai',await page.getByTestId('report-count').innerText()==='4 pesanan');const denied=await page.goto(base+'/pesanan/baru');ok('Pemilik tidak boleh input',denied.status()===403);
await page.setViewportSize({width:390,height:844});await page.goto(base+'/laporan?basis=selesai');ok('Tampilan mobile tidak meluap ke samping',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await shot('08_laporan_mobile');ok('Tanpa error JavaScript',errors.length===0);
fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify({timestamp:new Date().toISOString(),browser:browser.version(),order_code:code,checks,errors},null,2));console.log(JSON.stringify({order_code:code,passed:checks.length}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
