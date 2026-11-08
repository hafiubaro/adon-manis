// Uji browser teknis; bukan pengganti pengguna manusia untuk LKM 9.5.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{
const phase=process.env.M9_PHASE||'after';const out=path.resolve('evidence/module9');
const browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE_PATH?{executablePath:process.env.CHROMIUM_EXECUTABLE_PATH}:{}),args:JSON.parse(process.env.CHROMIUM_ARGS||'[]')});
const page=await browser.newPage({viewport:{width:1366,height:900}});const checks=[];
async function shot(n){await page.screenshot({path:path.join(out,phase+'_'+n+'.png'),fullPage:true});}
let base=process.env.APP_URL||'http://127.0.0.1:5000';
await page.goto(base+'/login');await page.locator('[name="_csrf"]').evaluate(el=>el.value='rusak-漢');await page.locator('#username').fill('admin');await page.locator('#password').fill('invalid');
let [r]=await Promise.all([page.waitForNavigation(),page.getByRole('button',{name:'Masuk ke ruang kerja'}).click()]);checks.push({tc:'TC19',http:r.status(),expected:phase==='before'?500:400});await shot('BUG01_csrf');
const outage=process.env.OUTAGE_URL||'http://127.0.0.1:5001';await page.goto(outage+'/login');await page.locator('#username').fill('admin');await page.locator('#password').fill('invalid');
[r]=await Promise.all([page.waitForNavigation(),page.getByRole('button',{name:'Masuk ke ruang kerja'}).click()]);checks.push({tc:'TC20',http:r.status(),expected:phase==='before'?500:503});await shot('BUG02_database');
await page.goto(base+'/login');await page.locator('#username').fill('admin');await page.locator('#password').fill(process.env.E2E_ADMIN_PASSWORD);await page.getByRole('button',{name:'Masuk ke ruang kerja'}).click();await page.waitForURL(base+'/');
await page.goto(base+'/pesanan?q=%25');const rowcount=await page.locator('tbody tr').count(),empty=await page.getByText('Tidak ada pesanan yang sesuai.',{exact:true}).count();checks.push({tc:'TC21',rows:empty?0:rowcount,expected:phase==='before'?10:0});await shot('BUG03_search');
if(phase==='after'){
 await page.goto(base+'/laporan?basis=selesai');checks.push({tc:'report',value:await page.getByTestId('report-value').innerText(),expected:'Rp180.000'});await shot('laporan');
 await page.setViewportSize({width:390,height:844});await page.goto(base+'/laporan');checks.push({tc:'mobile',overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),expected:false});await shot('mobile');
}
for(const c of checks){const actual=c.http??c.rows??c.value??c.overflow;c.capture_matches_expected=actual===c.expected;c.expected=({TC19:400,TC20:503,TC21:0})[c.tc]??c.expected;c.passed=actual===c.expected;if(!c.capture_matches_expected)throw Error(JSON.stringify(c));}
fs.writeFileSync(path.join(out,phase+'_browser.json'),JSON.stringify({phase,browser:browser.version(),checks},null,2));console.log(JSON.stringify(checks));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
