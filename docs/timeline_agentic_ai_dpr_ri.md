# Detail Day-to-Day Timeline Proyek Agentic AI --- DPR RI

Dokumen ini berisi rincian jadwal pelaksanaan harian (day-to-day
timeline) selama 6 bulan (120 hari kerja efektif) untuk proyek
pengembangan sistem **Agentic AI Klasifikasi Alat Kelengkapan Dewan
(AKD) & Analisis Sentimen** dengan arsitektur multi-agent berbasis
Gemini AI dan IndoBERT. Jadwal dipecah menjadi matriks bulanan untuk
mempermudah pemantauan progres dan ketertelusuran deliverables.

## Matriks Penanggung Jawab (PJ) Teknis

-   **Informatika 1 (Inf 1):** Fokus pada arsitektur backend,
    infrastruktur cloud, deployment, message broker, dan orkestrasi
    LangGraph.

-   **Informatika 2 (Inf 2):** Fokus pada implementasi model AI/NLP,
    local deployment IndoBERT, prompt engineering Gemini, dan evaluasi
    akurasi.

-   **Sistem Informasi 1 (SI 1):** Fokus pada desain skema database
    PostgreSQL, visualisasi dashboard Streamlit, dan automated PDF
    reporting.

-   **Sistem Informasi 2 (SI 2):** Fokus pada analisis sistem, pemodelan
    UML, penulisan dokumentasi teknis (PRD, SRS), dan penyusunan test
    cases QA.

## BULAN 1: Perencanaan Requirements, Kamus AKD, & Desain Arsitektur (Sprint 1 & 2)

  -------------------------------------------------------------------------
  **Hari**          **Kegiatan Utama** **Output /         **PJ Teknis**
                                       Deliverable**      
  ----------------- ------------------ ------------------ -----------------
  Hari 1            Kick-off meeting   Kesamaan pemahaman Semua Tim
                    internal dan       scope baseline     
                    penyelarasan visi  proyek.            
                    proyek bersama                        
                    seluruh anggota                       
                    tim.                                  

  Hari 2            Review fungsional  Catatan kesi apan  SI 2
                    requirements       implementasi fitur 
                    (FR-01 s.d FR-15)  sistem.            
                    dan batasan sistem                    
                    di dokumen awal.                      

  Hari 3            Pengumpulan data   Referensi mentah   SI 2
                    komponen 28 AKD    struktur           
                    aktif dan          organisasi dewan.  
                    pemahaman struktur                    
                    komisi DPR RI.                        

  Hari 4            Penyusunan kamus   Berkas konfigurasi Inf 2
                    deskripsi AKD      kamus AKD awal.    
                    berbasis                              
                    konfigurasi                           
                    dinamis dalam                         
                    bentuk JSON/YAML.                     

  Hari 5            Analisis format    Dokumen standar    SI 2
                    laporan harian     parameter evaluasi 
                    Sub. Analisis      sistem.            
                    Media DPR RI                          
                    sebagai acuan                         
                    ground truth.                         

  Hari 6            Kajian teknis      Pemetaan struktur  Inf 1
                    batas akses dan    data XML target    
                    struktur RSS feed  RSS feed.          
                    dari 12 media                         
                    online nasional                       
                    Tier 1.                               

  Hari 7            Eksperimen         Script             Inf 2
                    penarikan data     proof-of-concept   
                    Twitter/X          scraping Twitter.  
                    menggunakan                           
                    snscrape untuk                        
                    mode riset                            
                    akademik.                             

  Hari 8            Perhitungan        Dokumen estimasi   SI 1
                    simulasi biaya     anggaran bulanan   
                    token Gemini API & proyek.            
                    Cloud                                 
                    Infrastructure                        
                    (Skenario A s.d                       
                    B).                                   

  Hari 9            Penyusunan draf    Dokumen PRD dan    SI 2
                    akhir dokumen PRD  SRS final siap     
                    v3.0 dan SRS v3.0  tinjau.            
                    berstandar IEEE                       
                    830.                                  

  Hari 10           Sign-off dokumen   Persetujuan formal Semua Tim
                    persyaratan teknis dokumen            
                    dan persiapan      requirement.       
                    perpindahan menuju                    
                    Sprint 2.                             

  Hari 11           Pembuatan Use Case Diagram UML        SI 2
                    Diagram dan        perilaku sistem    
                    Activity Diagram   fungsional.        
                    untuk                                 
                    menggambarkan alur                    
                    sistem.                               

  Hari 12           Desain Class       Diagram UML        SI 2
                    Diagram dan        struktural         
                    Sequence Diagram   interaksi sistem.  
                    untuk                                 
                    menggambarkan                         
                    interaksi                             
                    multi-agent.                          

  Hari 13           Perancangan        Arsitektur graf    Inf 1
                    arsitektur         hubungan antar     
                    multi-agent system agen.              
                    menggunakan                           
                    framework                             
                    LangGraph.                            

  Hari 14           Perancangan skema  DDL skema tabel    SI 1
                    basis data         penampung data     
                    PostgreSQL untuk   mentah.            
                    entitas data                          
                    content_items dan                     
                    item_analysis.                        

  Hari 15           Perancangan tabel  DDL skema tabel    SI 1
                    akd_mapping        pemetaan           
                    (multi-label, maks klasifikasi.       
                    3) dan konfigurasi                    
                    modul pgvector.                       

  Hari 16           Desain tabel       DDL skema lengkap  SI 1
                    pendukung:         database           
                    trend_windows,     relasional.        
                    recommendations,                      
                    dan reports.                          

  Hari 17           Inisialisasi       Repositori backend Inf 1
                    repositori Git     fungsional awal.   
                    tim, standarisasi                     
                    kode, dan setup                       
                    proyek FastAPI                        
                    (Python 3.11+).                       

  Hari 18           Penyusunan         Berkas konfigurasi Inf 1
                    konfigurasi berkas deployment lokal.  
                    Docker Compose                        
                    untuk PostgreSQL                      
                    15, Redis 7+, dan                     
                    Celery.                               

  Hari 19           Pengujian          Environment        Inf 1
                    konektivitas       development lokal  
                    internal antara    tervalidasi.       
                    FastAPI,                              
                    PostgreSQL, dan                       
                    Redis cache di                        
                    lokal server.                         

  Hari 20           Evaluasi Milestone Dokumen            Semua Tim
                    Akhir Bulan 1      persetujuan cetak  
                    bersama Dosen      biru proyek.       
                    Pembimbing Skripsi                    
                    & Pembimbing                          
                    Magang.                               
  -------------------------------------------------------------------------

## BULAN 2: Pengembangan Data Collection Agents (Sprint 3)

  -----------------------------------------------------------------------
  **Hari**          **Kegiatan        **Output /        **PJ Teknis**
                    Utama**           Deliverable**     
  ----------------- ----------------- ----------------- -----------------
  Hari 21           Setup struktur    Kerangka modul    Inf 1
                    kode program      agen berita       
                    untuk News        online.           
                    Collection Agent                    
                    menggunakan                         
                    feedparser dan                      
                    requests.                           

  Hari 22           Pembuatan fungsi  Fungsi penarik    Inf 1
                    parsing XML RSS   komponen data     
                    feed untuk        berita.           
                    ekstraksi title,                    
                    content, url, dan                   
                    waktu rilis.                        

  Hari 23           Implementasi      Modul News Agent  Inf 1
                    konfigurasi URL   multi-target      
                    target untuk      fungsional.       
                    melakukan                           
                    crawling dari 12+                   
                    media nasional.                     

  Hari 24           Pengujian mandiri Laporan uji unit  SI 2
                    (unit testing)    News Collection   
                    pada News         Agent.            
                    Collection Agent                    
                    terhadap                            
                    stabilitas                          
                    parsing data                        
                    gratis.                             

  Hari 25           Integrasi fungsi  Data berita       SI 1
                    penyimpanan       online tersimpan  
                    otomatis News     di DB.            
                    Collection Agent                    
                    ke dalam database                   
                    PostgreSQL.                         

  Hari 26           Setup struktur    Kerangka modul    Inf 2
                    kode program      agen media        
                    untuk Twitter     sosial.           
                    Collection Agent                    
                    menggunakan modul                   
                    library snscrape.                   

  Hari 27           Pembuatan         Modul pencarian   Inf 2
                    parameter         data Twitter      
                    penarikan tweet   bertarget.        
                    berbasis kata                       
                    kunci (keyword                      
                    query) terkait                      
                    nama AKD.                           

  Hari 28           Implementasi      Modul Twitter     Inf 2
                    logika pembatasan Agent dengan      
                    volume penarikan  volume teratur.   
                    harian untuk                        
                    skenario pilot                      
                    kecil A2.                           

  Hari 29           Pengujian mandiri Laporan uji unit  SI 2
                    (unit testing)    Twitter Agent.    
                    Twitter Agent                       
                    terhadap potensi                    
                    error pemblokiran                   
                    / perubahan                         
                    aturan.                             

  Hari 30           Integrasi fungsi  Data tweet masuk  SI 1
                    penyimpanan       ke database       
                    otomatis Twitter  lokal.            
                    Collection Agent                    
                    ke dalam database                   
                    PostgreSQL.                         

  Hari 31           Pembuatan         Logika pembersih  SI 1
                    prosedur database data ganda        
                    untuk melakukan   otomatis.         
                    deduplikasi data                    
                    berdasarkan                         
                    kesamaan                            
                    URL/konten teks.                    

  Hari 32           Validasi          Data dual-source  SI 1
                    pengisian atribut terlabeli dengan  
                    penanda           rapi.             
                    source_type                         
                    (twitter atau                       
                    news_online) di                     
                    database.                           

  Hari 33           Konfigurasi Redis Sistem broker     Inf 1
                    sebagai antrean   antrean pesan     
                    tugas (message    aktif.            
                    broker) serta                       
                    inisialisasi                        
                    Celery task.                        

  Hari 34           Implementasi      Penjadwal         Inf 1
                    skrip Celery Beat otomatisasi agen  
                    untuk otomatisasi aktif.            
                    eksekusi                            
                    pengumpulan data                    
                    berkala setiap 4                    
                    jam.                                

  Hari 35           Pengujian         Alur pengumpulan  SI 2
                    integrasi         data paralel      
                    (integration      stabil.           
                    testing)                            
                    pengumpulan data                    
                    dual-source                         
                    secara bersamaan.                   

  Hari 36-37        Implementasi      Kode program yang Inf 1
                    penanganan        tangguh terhadap  
                    kesalahan (error  error.            
                    handling) saat                      
                    terjadi gangguan                    
                    jaringan atau RSS                   
                    mati.                               

  Hari 38-39        Pemberantasan     Pipeline          Inf 2
                    data mentah (data pembersih teks    
                    preprocessing)    terintegrasi.     
                    dari karakter                       
                    sampah dan teks                     
                    iklan media                         
                    online.                             

  Hari 40           Review Sprint 3:  Persetujuan       Semua Tim
                    Validasi volume   kelayakan data    
                    data mentah       mentah.           
                    terkumpul di                        
                    database bersama                    
                    pembimbing                          
                    magang.                             
  -----------------------------------------------------------------------

## BULAN 3: NLP Sentimen & Klasifikasi AKD Gemini (Sprint 4)

  --------------------------------------------------------------------------------------------------------
  **Hari**          **Kegiatan Utama**                                **Output /         **PJ Teknis**
                                                                      Deliverable**      
  ----------------- ------------------------------------------------- ------------------ -----------------
  Hari 41           Pengunduhan dan setup lokal model                 Model IndoBERT     Inf 2
                    mdhugol/indonesia-bert-sentiment-classification   terunduh di        
                    dari HuggingFace.                                 server.            

  Hari 42           Pembuatan fungsi preprocessing khusus Bahasa      Fungsi penyiapan   Inf 2
                    Indonesia (case folding, filtering kata tak       teks untuk         
                    baku).                                            IndoBERT.          

  Hari 43           Koding fungsi klasifikasi sentimen otomatis       Pipeline analisis  Inf 2
                    (positif, negatif, netral) per baris data.        sentimen IndoBERT. 

  Hari 44           Pengujian akurasi awal sentimen menggunakan       Laporan            SI 2
                    sampel data berlabel dari dataset terbuka.        profesi/performa   
                                                                      awal IndoBERT.     

  Hari 45           Integrasi penyimpanan otomatis hasil label        Data teranalisis   SI 1
                    sentimen ke tabel database item_analysis.         sentimen di DB.    

  Hari 46           Setup integrasi koneksi endpoint pihak ketiga     Modul konektor     Inf 1
                    menggunakan kredensial resmi Gemini API.          Gemini API aktif.  

  Hari 47           Perancangan prompt engineering zero-shot awal     Berkas teks prompt Inf 2
                    untuk mendeteksi 3-5 AKD prioritas fase pilot.    klasifikasi AKD.   

  Hari 48           Implementasi kode Analysis Agent untuk pemetaan   Pipeline           Inf 2
                    multi-label zero-shot Gemini (maks 3 label).      klasifikasi AKD    
                                                                      zero-shot.         

  Hari 49           Koding fungsi pengekstraksi nilai confidence      Ekstraktor nilai   Inf 2
                    score dan nomor urut ranking dari respons JSON    kepastian model    
                    Gemini.                                           AI.                

  Hari 50           Integrasi penyimpanan data pemetaan hasil         Data pemetaan      SI 1
                    klasifikasi AKD ke tabel database akd_mapping.    komisi dewan di    
                                                                      DB.                

  Hari 51           Pengumpulan contoh data berlabel manual dari      Dataset acuan      SI 2
                    berkas asli Sub. Analisis Media DPR RI.           pembanding (ground 
                                                                      truth).            

  Hari 52           Koding fungsi komparasi otomatis untuk menghitung Script evaluator   Inf 2
                    ketepatan prediksi AI vs data manual.             performa           
                                                                      klasifikasi.       

  Hari 53           Pengujian akurasi sistem terhadap target akurasi  Matriks capaian    SI 2
                    sentimen \>= 75-80% & AKD top-1 \>= 70%.          kualitas           
                                                                      klasifikasi AI.    

  Hari 54           Iterasi perbaikan instruksi prompt dan penyusunan Prompt Gemini      Inf 2
                    contoh few-shot untuk menaikkan akurasi model.    versi optimasi.    

  Hari 55           Penerapan arsitektur batching data dan caching    Logika efisiensi   Inf 1
                    token respons untuk menekan pembengkakan biaya    pengeluaran token. 
                    API.                                                                 

  Hari 56-57        Uji jalan komprehensif Analysis Agent secara      Aliran analisis    SI 2
                    end-to-end pada aliran data harian riil.          data berjalan      
                                                                      otomatis.          

  Hari 58-59        Koding mekanisme proteksi sistem saat kuota API   Kode pengaman      Inf 1
                    Gemini habis atau server mengalami kegagalan      kegagalan koneksi  
                    respons.                                          API.               

  Hari 60           Evaluasi Akhir Bulan 3 / Akhir Fase 1 Pilot untuk Dokumen hasil      Semua Tim
                    menentukan keputusan lanjut menuju perluasan      evaluasi performa  
                    sistem.                                           pilot.             
  --------------------------------------------------------------------------------------------------------

## BULAN 4: Orkestrasi Multi-Agent & Deteksi Tren Anomali (Sprint 5)

  ----------------------------------------------------------------------------
  **Hari**          **Kegiatan Utama**     **Output /        **PJ Teknis**
                                           Deliverable**     
  ----------------- ---------------------- ----------------- -----------------
  Hari 61           Inisialisasi pustaka   Struktur graf     Inf 1
                    framework LangGraph    sistem            
                    dan penyusunan         multi-agent.      
                    struktur graph agen                      
                    utama.                                   

  Hari 62           Registrasi node fungsi Node fungsional   Inf 1
                    penarik data dan node  terdaftar di      
                    fungsi analisis ke     LangGraph.        
                    dalam graph sistem.                      

  Hari 63           Implementasi           Supervisor Agent  Inf 1
                    Supervisor Agent       fungsional aktif. 
                    sebagai pengendali                       
                    pusat alur eksekusi                      
                    dan perpindahan state                    
                    data.                                    

  Hari 64           Pengujian alur         Alur data         SI 2
                    komunikasi data antar  multi-agent       
                    agen di bawah          tervalidasi.      
                    koordinasi penuh                         
                    Supervisor Agent.                        

  Hari 65           Refactoring kode       Sistem            Inf 1
                    manajemen memori graph multi-agent yang  
                    agar transisi data     efisien memori.   
                    asinkron tidak                           
                    membebani RAM server.                    

  Hari 66           Setup dan load model   Model embedding   Inf 2
                    embedding              aktif di sistem.  
                    multilingual-e5-base                     
                    untuk mengubah teks                      
                    menjadi representasi                     
                    vektor.                                  

  Hari 67           Koding fungsi          Fungsi query      SI 1
                    penarikan agregasi     agregator data    
                    data historis          volume.           
                    berdasarkan rentang                      
                    waktu harian/mingguan.                   

  Hari 68           Koding algoritma       Engine penghitung Inf 2
                    statistik rolling      z-score           
                    z-score untuk          volumetrik.       
                    menghitung pergeseran                    
                    volume isu per AKD.                      

  Hari 69           Implementasi batasan   Trend Agent       Inf 2
                    angka threshold        penentu anomali   
                    statistik untuk        isu.              
                    menetapkan status                        
                    anomali pada Trend                       
                    Agent.                                   

  Hari 70           Integrasi penyimpanan  Rekam jejak       SI 1
                    hasil kalkulasi        kalkulasi tren di 
                    statistik pergerakan   DB.               
                    tren ke tabel database                   
                    trend_windows.                           

  Hari 71           Pembuatan fungsi       Mekanisne         Inf 1
                    interupsi pemicu alert interupsi pemicu  
                    otomatis saat          alert.            
                    terdeteksi lonjakan                      
                    angka z-score anomali.                   

  Hari 72           Pengujian fungsi       Laporan presisi   SI 2
                    deteksi anomali untuk  pendeteksian      
                    mengejar target        anomali.          
                    precision alert \>=                      
                    70%.                                     

  Hari 73           Sinkronisasi berkala   Data tren         SI 1
                    data luaran Trend      terintegrasi di   
                    Agent ke dalam antrean database.         
                    database utama.                          

  Hari 74-76        Pengujian beban        Laporan performa  SI 2
                    (stress testing) pada  batas atas        
                    pipeline gabungan      sistem.           
                    LangGraph + Trend                        
                    Agent dengan data                        
                    simulasi besar.                          

  Hari 77-79        Perbaikan bug pada     Kode perhitungan  Inf 1
                    penanganan bentrokan   statistik yang    
                    data asinkronus saat   stabil.           
                    menghitung rolling                       
                    window harian.                           

  Hari 80           Review Sprint 5:       Persetujuan modul Semba Tim
                    Demonstrasi stabilitas orkestrasi &      
                    deteksi tren anomali   tren.             
                    di hadapan tim                           
                    pengembang.                              
  ----------------------------------------------------------------------------

## BULAN 5: Rangkuman Naratif, Dokumen PDF, & Antarmuka Dashboard (Sprint 6 & 7)

  --------------------------------------------------------------------------
  **Hari**          **Kegiatan Utama** **Output /          **PJ Teknis**
                                       Deliverable**       
  ----------------- ------------------ ------------------- -----------------
  Hari 81           Pembuatan          Prompt rangkuman    Inf 2
                    instruksi khusus   berita komisi       
                    prompt             dewan.              
                    summarization teks                     
                    berita/tweet                           
                    memakai Gemini 2.5                     
                    Flash.                                 

  Hari 82           Implementasi       Narasi summary      Inf 2
                    Insight Agent      otomatis per AKD.   
                    untuk menyusun                         
                    narasi ringkasan                       
                    eksekutif otomatis                     
                    per komisi/AKD.                        

  Hari 83           Pengujian          Ringkasan teks      SI 2
                    keterbacaan dan    tervalidasi layak   
                    relevansi hasil    baca.               
                    ringkasan teks                         
                    yang diproduksi                        
                    oleh Insight                           
                    Agent.                                 

  Hari 84           Perancangan prompt Prompt generator    Inf 2
                    perumusan draf     draf rekomendasi.   
                    saran aksi                             
                    kebijakan                              
                    berdasarkan                            
                    kumpulan intisari                      
                    isu aktual.                            

  Hari 85           Implementasi       Agen perumus        Inf 2
                    Recommendation     rekomendasi         
                    Agent menggunakan  fungsional.         
                    kombinasi Gemini                       
                    2.5 Flash dan                          
                    review interface.                      

  Hari 86           Pembuatan skema    Alur data           SI 1
                    kolom status       persetujuan         
                    terstruktur        terealisasi di DB.  
                    meliputi tipe data                     
                    state draft,                           
                    reviewed, dan                          
                    published.                             

  Hari 87           Pembangunan sistem Log audit           SI 1
                    pencatatan log     peninjauan          
                    audit otomatis     tersimpan di DB.    
                    untuk merekam                          
                    riwayat verifikasi                     
                    user peninjau.                         

  Hari 88           Pengujian          Alur kerja          SI 2
                    fungsionalitas     human-in-the-loop   
                    alur persetujuan   tervalidasi.        
                    draf rekomendasi                       
                    kebijakan dari                         
                    status awal s.d                        
                    siap publikasi.                        

  Hari 89           Penerapan          Hak akses endpoint  Inf 1
                    Role-Based Access  server terproteksi. 
                    Control (RBAC)                         
                    untuk mengunci                         
                    endpoint server                        
                    sesuai kelas hak                       
                    akses user.                            

  Hari 90           Integrasi          Database            SI 1
                    menyeluruh luaran  rekomendasi         
                    fungsi Sprint 6 ke terintegrasi penuh. 
                    dalam skema tabel                      
                    database                               
                    recommendations.                       

  Hari 91-92        Tinjauan internal  Validasi kesiapan   Semua Tim
                    berkala untuk      pasokan data        
                    memastikan pasokan sistem.             
                    data untuk                             
                    dashboard dan                          
                    berkas cetak PDF                       
                    siap dikonsumsi.                       

  Hari 93           Setup struktur     Kerangka dasar      SI 1
                    folder aplikasi,   aplikasi dashboard  
                    inisialisasi       visual.             
                    framework                              
                    Streamlit, dan                         
                    penentuan skema                        
                    warna antarmuka.                       

  Hari 94           Koding visualisasi Antarmuka visual    SI 1
                    diagram tren       analitik Streamlit  
                    volume, grafik     harian.             
                    sentimen harian,                       
                    dan tabel urutan                       
                    Top 10 AKD.                            

  Hari 95           Pembuatan tombol   Panel verifikasi    SI 1
                    fungsional dan     reviewer            
                    halaman khusus     fungsional.         
                    bagi Reviewer                          
                    untuk aksi                             
                    approve/reject                         
                    draf rekomendasi.                      

  Hari 96           Hubung-kait        Dashboard analitik  SI 1
                    antarmuka visual   real-time aktif     
                    dashboard          penuh.              
                    Streamlit dengan                       
                    database                               
                    PostgreSQL dan                         
                    Redis cache.                           

  Hari 97           Setup pustaka      Komponen engine     SI 1
                    ekspor dokumen pdf cetak berkas PDF.   
                    menggunakan                            
                    utilitas library                       
                    ReportLab atau                         
                    WeasyPrint.                            

  Hari 98           Pembuatan tata     Template digital    SI 1
                    letak (layout      laporan PDF resmi   
                    design) berkas PDF harian.             
                    agar serupa dengan                     
                    pola cetak fisik                       
                    milik DPR RI.                          

  Hari 99           Koding penulisan   Fungsi pembuat      SI 1
                    otomatis data      berkas PDF          
                    komponen indeks    otomatis.           
                    harian, tabel                          
                    alert anomali, dan                     
                    lampiran saran isu                     
                    ke PDF.                                

  Hari 100          Pengujian          Sistem generator    Inf 1
                    pembuatan berkas   PDF terjadwal       
                    PDF harian         aktif.              
                    otomatis yang                          
                    digerakkan lewat                       
                    instruksi                              
                    penjadwalan Celery                     
                    beat.                                  

  Hari 101-102      Optimasi kecepatan Skrip generator PDF SI 1
                    pemrosesan data    performa tinggi.    
                    cetak laporan agar                     
                    durasi pengerjaan                      
                    \<= 5 menit                            
                    tercapai.                              

  Hari 103          Pengujian          Integrasi visual &  SI 2
                    fungsionalitas     dokumen             
                    keterkaitan data   tervalidasi.        
                    antara antarmuka                       
                    dashboard visual                       
                    dengan file                            
                    unduhan laporan                        
                    PDF.                                   

  Hari 104          Review Sprint 7:   Persetujuan modul   Semua Tim
                    Demonstrasi visual visual & cetak PDF. 
                    dashboard dan                          
                    pembagian sampel                       
                    dokumen cetak                          
                    laporan PDF ke                         
                    internal tim.                          
  --------------------------------------------------------------------------

## BULAN 6: Pengujian Sistem End-to-End, QA, & Serah Terima Proyek (Sprint 8)

  --------------------------------------------------------------------------
  **Hari**          **Kegiatan Utama**   **Output /        **PJ Teknis**
                                         Deliverable**     
  ----------------- -------------------- ----------------- -----------------
  Hari 105          Penyusunan draf      Berkas dokumen    SI 2
                    lembar skenario      skenario          
                    pengujian menyeluruh pengujian SIT.    
                    (System Integration                    
                    Testing / SIT).                        

  Hari 106          Eksekusi uji SIT     Laporan catatan   SI 2
                    end-to-end: dari     temuan hasil uji  
                    penarikan data       SIT.              
                    mentah -\> analisis                    
                    model AI -\>                           
                    visualisasi -\>                        
                    cetak PDF.                             

  Hari 107-109      Proses perbaikan     Kode program      Inf 1 & Inf 2
                    kesalahan            sistem bebas bug  
                    pemrograman (bug     kritis.           
                    fixing) atas temuan                    
                    kegagalan fungsi di                    
                    masa pengujian SIT.                    

  Hari 110          Pengujian validasi   Dashboard aman    SI 2
                    penutupan identitas  dari kebocoran    
                    pribadi berupa       data privasi.     
                    pembersihan username                   
                    Twitter pada visual                    
                    dashboard.                             

  Hari 111          Pembuatan materi     Berkas kuesioner  SI 2
                    instrumen kuesioner  pengujian SUS     
                    pengujian kegunaan   standar.          
                    aplikasi memakai                       
                    standar kriteria                       
                    System Usability                       
                    Scale (SUS).                           

  Hari 112          Pelaksanaan          Data mentah       SI 1
                    Usability Testing    jawaban kuesioner 
                    mandiri bersama      user.             
                    perwakilan staf                        
                    analitik dari Sub.                     
                    Analisis Media DPR                     
                    RI.                                    

  Hari 113          Rekapitulasi nilai   Dokumen hasil     SI 2
                    kepuasan user dengan capaian nilai uji 
                    target capaian skor  SUS.              
                    akhir pengujian SUS                    
                    \>= 68.                                

  Hari 114          Penyusunan laporan   Dokumen laporan   SI 2
                    rangkuman akhir      testing final     
                    penutupan pengujian  komplit.          
                    keandalan serta                        
                    kualitas fungsional                    
                    aplikasi.                              

  Hari 115          Rekonsiliasi         Laporan           SI 1
                    keuangan atas dana   kesesuaian        
                    riil sewa cloud      anggaran          
                    infrastructure       pengeluaran.      
                    DigitalOcean dan                       
                    tagihan kuota token                    
                    Gemini API.                            

  Hari 116          Kajian akhir         Berkas jaminan    SI 2
                    keselarasan sistem   kepatuhan         
                    terhadap aturan      regulasi data.    
                    legalitas Terms of                     
                    Service sumber data                    
                    serta kepatuhan UU                     
                    PDP.                                   

  Hari 117          Penyusunan buku      Dokumen panduan   SI 2
                    petunjuk penggunaan  teknis            
                    (user manual guide), operasional       
                    dokumentasi          sistem.           
                    arsitektur teknik,                     
                    dan kamus data                         
                    komplit.                               

  Hari 118          Finalisasi berkas    Dokumen skripsi   Semua Tim
                    bundel dokumen       dan laporan       
                    pertanggungjawaban   magang final.     
                    proyek magang                          
                    instansional serta                     
                    draf karya ilmiah                      
                    skripsi.                               

  Hari 119          Presentasi hasil     Penilaian formal  Semua Tim
                    demo kerja sistem di performa hasil    
                    hadapan jajaran      kerja tim.        
                    dosen pembimbing                       
                    akademis dan                           
                    pimpinan pembimbing                    
                    magang.                                

  Hari 120          Serah terima berkas  Penutupan formal  Semua Tim
                    aplikasi secara      proyek Fase 1     
                    formal (handover),   Pilot.            
                    penandatanganan                        
                    berita acara, dan                      
                    rapat pleno                            
                    keputusan ekspansi                     
                    Fase 2.                                
  --------------------------------------------------------------------------
